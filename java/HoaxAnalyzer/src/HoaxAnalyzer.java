import org.json.simple.JSONArray;
import org.json.simple.JSONObject;

import java.io.*;
import java.util.*;

/**
 * Created by Tifani on 3/12/2017.
 */
public class HoaxAnalyzer {
    public static final String FEATURE = "feature";

    public static void createModel() throws IOException {
        String factOrHoax = "fact";
        String dir = "E:\\GitHub\\hoax-analyzer-ml\\dataset\\idn-" + factOrHoax;
        File folder = new File(dir);
        File[] listOfFiles = folder.listFiles();

        String csvFile = "E:\\GitHub\\hoax-analyzer-ml\\idn-" + factOrHoax + ".csv";
        FileWriter writer = new FileWriter(csvFile);

        ArrayList<String> line = new ArrayList<>();
        line.add("filename");
        line.add("text");
        for(int i = 0; i < FeatureExtractor.acceptibleTag.size(); i++) {
            String tag = FeatureExtractor.acceptibleTag.get(i).toLowerCase();
            for(int j = 1; j <= 8; j++) {
                line.add(tag + j + "_token");
                line.add(tag + j + "_prob");
                line.add(tag + j + "_wcount");
                line.add(tag + j + "_wpos");
                line.add(tag + j + "_spos");
            }
            line.add(tag + "_class");
        }
        CSVUtil.writeLine(writer, line);

        for (File file : listOfFiles) {
            if (file.isFile()) {
                String filename = dir + "\\" + file.getName();
                System.out.println(filename);

                String text = HoaxUtil.loadFile(filename);
                HashMap<String, HashMap<String, WordFeature>> wordTag = FeatureExtractor.extractTag(text);
                CSVUtil.writeToCSV(writer, factOrHoax + "-" + file.getName(), text, wordTag);
                System.out.println("done!");
                System.out.println();
            }
        }
        writer.flush();
        writer.close();
    }

    public static JSONObject createJSON(HashMap<String, HashMap<String, WordFeature>> wordTag) {
        JSONObject object = new JSONObject();
        Iterator<Map.Entry<String, HashMap<String, WordFeature>>> it = wordTag.entrySet().iterator();
        while (it.hasNext()) {
            Map.Entry<String, HashMap<String, WordFeature>> pair = it.next();
            HashMap<String, WordFeature> key = pair.getValue();
            Iterator<Map.Entry<String, WordFeature>> itKey = key.entrySet().iterator();

            JSONArray feature = new JSONArray();
            while (itKey.hasNext()) {
                Map.Entry<String, WordFeature> pairKey = itKey.next();
                feature.add(pairKey.getValue().toJSONObject());
                itKey.remove();
            }

            object.put(pair.getKey(), feature);
            it.remove(); // avoids a ConcurrentModificationException
        }

        return object;
    }

    public static void main (String[] args) throws IOException {
        // Avoid printing anything :(
        PrintStream originalStream = System.out;
        PrintStream dummyStream    = new PrintStream(new OutputStream(){
            public void write(int b) {
                //NO-OP
            }
        });
        System.setOut(dummyStream);

        // HoaxAnalyzer.createModel();
        String filename = "E:\\GitHub\\hoax-analyzer-ml\\dataset\\idn-hoax\\1.txt";
        // String filename = args[0];

        String text = HoaxUtil.loadFile(filename);
        HashMap<String, HashMap<String, WordFeature>> wordTag = FeatureExtractor.extractTag(text);


        System.setOut(originalStream);
        System.out.println(createJSON(wordTag).toJSONString());
        System.setOut(dummyStream);
    }
}

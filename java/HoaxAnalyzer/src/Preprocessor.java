import IndonesianNLP.*;
import com.sun.deploy.util.StringUtils;

import java.io.*;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Created by Tifani on 3/12/2017.
 */
public class Preprocessor {
    private static final ArrayList<String> STOPWORDS = initStopwords();

    private static ArrayList<String> initStopwords() {
        ArrayList<String> idnStopwords = new ArrayList<>();
        String filePath = System.getProperty("user.dir") + "/resource/formalization/stopword.txt";
        fileToArray(idnStopwords, filePath);
        filePath = System.getProperty("user.dir") + "/resource/formalization/hoax-stopwords.txt";
        fileToArray(idnStopwords, filePath);
        return idnStopwords;
    }

    private static void fileToArray(ArrayList<String> idnStopwords, String filePath) {
        BufferedReader in = null;
        try {
            in = new BufferedReader(new FileReader(filePath));
        } catch (FileNotFoundException e) {
            e.printStackTrace();
        }
        String str;

        try {
            while((str = in.readLine()) != null){
                idnStopwords.add(str);
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public static String preprocess(String text) {
        text = preprocessMoney(text);

        IndonesianSentenceTokenizer tokenizer = new IndonesianSentenceTokenizer();
        ArrayList<String> tokens = new ArrayList<>();
        tokens.addAll(tokenizer.tokenizeSentence(text));

        IndonesianSentenceFormalization formalizer = new IndonesianSentenceFormalization();
        for (int i = 0; i < tokens.size(); i++) {
            tokens.set(i, formalizer.formalizeWord(tokens.get(i)));

            // For the beginning of the sentence
            String oldString = tokens.get(i);
            String newString = formalizer.formalizeWord(tokens.get(i).toLowerCase());
            if (newString.length() > oldString.length()) {
                tokens.set(i, newString);
            }
            if (tokens.get(i).length() > 1) {
                tokens.set(i, tokens.get(i).replace(".", ""));
            }
            // System.out.print(tokens.get(i) + "|");
            if(STOPWORDS.contains(tokens.get(i).toLowerCase())) {
                tokens.set(i, "");
            }
        }
        // System.out.println();

        String processedText = StringUtils.join(tokens, " ");
        // System.out.println(processedText);
        formalizer.initStopword();
        processedText = formalizer.deleteStopword(processedText);
        // System.out.println(processedText);

        return processedText;
    }

    private static String preprocessMoney(String text) {
        Pattern phone = Pattern.compile("([0-9])*rb+");
        Matcher action = phone.matcher(text);
        StringBuffer sb = new StringBuffer(text.length());
        while (action.find()) {
            String match = action.group(1);
            if (match != null) {
                match.replace("rb", " ribu");
                action.appendReplacement(sb, match);
            }
        }

        action.appendTail(sb);
        return sb.toString();
    }

    public static ArrayList<String[]> tagging(String text) {
        // Avoid printing something from pos tag :(
        PrintStream originalStream = System.out;
        PrintStream dummyStream    = new PrintStream(new OutputStream(){
            public void write(int b) {
                //NO-OP
            }
        });

        System.setOut(dummyStream);
        String processedText = preprocess(text);
        IndonesianPOSTagger tagger = new IndonesianPOSTagger();
        ArrayList<String[]> posTag = tagger.doPOSTag(processedText);
        System.setOut(originalStream);

        return posTag;
    }

    public void nyaw() {
        String sentence = "Soekarno dilahirkan di Surabaya Jawa Timur pada 6 Juni 1901 dan meninggal di Jakarta pada 21 Juni 1970 adalah Presiden Indonesia pertama yang menjabat pada periode 1945-1966";
        IndonesianPOSTagger idPOSTagger = new IndonesianPOSTagger();
        ArrayList<String[]> posTag = idPOSTagger.doPOSTag(sentence);
        for(int i = 0; i < posTag.size(); i++){
            System.out.println(posTag.get(i)[0] + " - " + posTag.get(i)[1]);
        }
    }


}

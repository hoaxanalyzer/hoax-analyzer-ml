import com.sun.deploy.util.StringUtils;

import java.io.File;
import java.io.IOException;
import java.nio.charset.Charset;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.List;

/**
 * Created by Tifani on 3/24/2017.
 */
public class HoaxUtil {
    private static Charset encoding = Charset.defaultCharset();

    public static String loadFile(String path) throws IOException {
        List<String> lines = Files.readAllLines(Paths.get(path), encoding);
        return StringUtils.join(lines, " ").replaceAll("\\P{InBasic_Latin}", " ").replace("”"," ").replace("”"," ");
    }
}

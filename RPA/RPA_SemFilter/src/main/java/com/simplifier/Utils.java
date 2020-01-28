package com.simplifier;

import com.opencsv.*;

import java.io.*;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;
import java.util.stream.Collectors;

/**
 * Utils is the class for reading the log from a CSV file to <code>HashMap</code>,
 * where the key is a caseId of the action and the value is <code>StringBuilder</code>
 * that contains all actions with corresponding caseId, and also for writing the result
 * of simplification to the CSV file.
 */
public class Utils {

    /**
     * This method is used for writing the log from to the file.
     */
    public static void writeDataLineByLine(String filePath, String data) {
        try {
            CSVWriter writer = new CSVWriter(new FileWriter(filePath),
                    CSVWriter.DEFAULT_SEPARATOR,
                    CSVWriter.NO_QUOTE_CHARACTER,
                    CSVWriter.NO_ESCAPE_CHARACTER,
                    CSVWriter.RFC4180_LINE_END);

            String[] headers = {"\"caseID\"", "\"timeStamp\"", "\"userID\"", "\"targetApp\"", "\"eventType\"", "\"url\"",
                    "\"content\"", "\"target.workbookName\"", "\"target.sheetName\"", "\"target.id\"", "\"target.class\"",
                    "\"target.tagName\"", "\"target.type\"", "\"target.name\"", "\"target.value\"", "\"target.innerText\"",
                    "\"target.checked\"", "\"target.href\"", "\"target.option\"", "\"target.title\"", "\"target.innerHTML\""
            };

            writer.writeNext(headers);
            writeActionsValues(writer, data);

            writer.close();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private static void writeActionsValues(CSVWriter writer, String data) {
        String[] actions = data.split("\n");

        for (String action : actions) {
            String[] actionValues = action.split(",(?=(?:[^\"]*\"[^\"]*\")*[^\"]*$)", -1);
            actionValues = Arrays.stream(actionValues)
//                    .map(e -> e.replaceAll("\"{2}(([^\"]|\"\")*)\"{2}", "\"\"\"$1\"\"\""))
                    .toArray(String[]::new);
            writer.writeNext(actionValues);
        }
    }

    /**
     * This method is used for reading the log from the file.
     *
     * @param filePath the location of the log
     * @return Map, where the key is a caseId of the log and the value is
     * <code>StringBuilder</code> that contains all actions with
     * corresponding caseId
     */
    public Map<String, StringBuilder> readLogFromFile(String filePath) {
        Map<String, StringBuilder> cases = new HashMap<>();

        try {
            RFC4180Parser rfc4180Parser = new RFC4180ParserBuilder().withQuoteChar('\"').build();
            BufferedReader fileReader = new BufferedReader(new InputStreamReader(new FileInputStream(filePath)));
            CSVReader csvReader = new CSVReaderBuilder(fileReader)
                    .withSkipLines(1)
                    .withCSVParser(rfc4180Parser)
                    .build();

            createActionsMap(csvReader, cases);

            csvReader.close();
            fileReader.close();
        } catch (Exception e) {
            e.printStackTrace();
        }

        return cases;
    }

    private void createActionsMap(CSVReader csvReader, Map<String, StringBuilder> cases) throws IOException {
        String[] nextLine;

        while ((nextLine = csvReader.readNext()) != null) {
            String caseId = nextLine[0] == null ? "undefined" : String.format("\"%s\"", nextLine[0]);
            cases.putIfAbsent(caseId, new StringBuilder());

            String[] actionValuesWithoutCaseId = Arrays.copyOfRange(nextLine, 1, nextLine.length);
            String action = Arrays.stream(actionValuesWithoutCaseId)
                    .map(e -> {
                        e = e.replaceAll("\"", "\"\"");
                        e = String.format("\"%s\"", e);
                        return e;
                    })
                    .collect(Collectors.joining(","));

            cases.get(caseId).append(action).append("\n");
        }
    }
}

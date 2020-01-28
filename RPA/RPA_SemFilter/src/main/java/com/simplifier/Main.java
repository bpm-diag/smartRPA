package com.simplifier;

import com.simplifier.pre_processing.PreProcessing;
import com.simplifier.rules.navigation.NavigationSimplifier;
import com.simplifier.rules.read.ReadSimplifier;
import com.simplifier.rules.write.WriteSimplifier;
import com.simplifier.validation.Validator;
import org.apache.commons.lang3.StringUtils;

import java.util.Arrays;
import java.util.Comparator;
import java.util.Map;
import java.util.stream.Collectors;

public class Main {

    public static void main(String[] args) {
        String filePath = args[0];
        Utils utils = new Utils();
        Map<String, StringBuilder> cases = utils.readLogFromFile(filePath);
        Map<String, String> result = cases.entrySet().stream()
                .collect(Collectors.toMap(Map.Entry::getKey, logCase -> {
                    String logs = logCase.getValue().toString();
                    return applySimplifier(logs);
                }));
        String writableLog = result.entrySet().stream()
                .map(e -> Arrays.stream(e.getValue().split("\\r?\\n"))
                        .map(v -> e.getKey() + "," + v + "\n")
                        .collect(Collectors.joining()))
                .collect(Collectors.joining());

        String[] sortedLog = writableLog.split("\\r?\\n");
        Arrays.sort(sortedLog, Comparator.comparing(s -> s.substring(2)));

        System.out.println("Result\n");
        System.out.println(StringUtils.join(Arrays.asList(sortedLog), "\n"));

        String newFilePath = filePath.substring(0, filePath.lastIndexOf(".")) + "_filtered.csv";
        Utils.writeDataLineByLine(newFilePath, StringUtils.join(Arrays.asList(sortedLog), "\n"));
    }

    private static String applySimplifier(String log) {
        try {
            Validator.validateForIdOrName(log);

            String sortedLog = PreProcessing.sortLog(log);
            System.out.println("SORTED LOG\n");
            System.out.println(sortedLog);

            sortedLog = PreProcessing.deleteChromeClipboardCopy(sortedLog);
            sortedLog = PreProcessing.mergeNavigationCellCopy(sortedLog);
            sortedLog = PreProcessing.identifyPasteAction(sortedLog);
            System.out.println("AFTER PRE PROCESSING\n");
            System.out.println(sortedLog);

            while (ReadSimplifier.containsRedundantCopy(sortedLog) ||
                    ReadSimplifier.containsSingleCopy(sortedLog) ||
                    NavigationSimplifier.containsRedundantClickTextField(sortedLog) ||
                    WriteSimplifier.containsRedundantDoublePaste(sortedLog) ||
                    WriteSimplifier.containsRedundantEditCell(sortedLog) ||
                    WriteSimplifier.containsRedundantEditField(sortedLog) ||
                    WriteSimplifier.containsRedundantPasteIntoCell(sortedLog) ||
                    WriteSimplifier.containsRedundantPasteIntoRange(sortedLog) ||
                    WriteSimplifier.containsRedundantDoubleEditField(sortedLog)) {

                sortedLog = ReadSimplifier.removeRedundantCopy(sortedLog);
                System.out.println("ReadSimplifier.removeRedundantCopy\n");
                System.out.println(sortedLog);

                sortedLog = ReadSimplifier.removeSingleCopy(sortedLog);
                System.out.println("After ReadSimplifier.removeSingleCopy\n");
                System.out.println(sortedLog);

                sortedLog = NavigationSimplifier.removeRedundantClickTextField(sortedLog);
                System.out.println("After NavigationSimplifier.removeRedundantClickTextField\n");
                System.out.println(sortedLog);

                sortedLog = WriteSimplifier.removeRedundantDoublePaste(sortedLog);
                System.out.println("After WriteSimplifier.removeRedundantDoublePaste\n");
                System.out.println(sortedLog);

                sortedLog = WriteSimplifier.removeRedundantEditCell(sortedLog);
                System.out.println("After WriteSimplifier.removeRedundantEditCell\n");
                System.out.println(sortedLog);

                sortedLog = WriteSimplifier.removeRedundantEditField(sortedLog);
                System.out.println("After WriteSimplifier.removeRedundantEditField\n");
                System.out.println(sortedLog);

                sortedLog = WriteSimplifier.removeRedundantPasteIntoCell(sortedLog);
                System.out.println("After WriteSimplifier.removeRedundantPasteIntoCell\n");
                System.out.println(sortedLog);

                sortedLog = WriteSimplifier.removeRedundantPasteIntoRange(sortedLog);
                System.out.println("After WriteSimplifier.removeRedundantPasteIntoRange\n");
                System.out.println(sortedLog);

                sortedLog = WriteSimplifier.removeRedundantDoubleEditField(sortedLog);
                System.out.println("After WriteSimplifier.removeRedundantDoubleEditField\n");
                System.out.println(sortedLog);
            }

            return sortedLog;

        } catch (Exception e) {
            e.printStackTrace();
        }

        return log;
    }
}

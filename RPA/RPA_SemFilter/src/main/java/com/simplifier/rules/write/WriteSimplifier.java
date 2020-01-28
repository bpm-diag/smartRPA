package com.simplifier.rules.write;

import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * This class consists of methods that operate on the log:
 * check if the log contains redundant write actions, and if so,
 * remove them and return a new log.
 * <br><br>
 * <h2>List of "Write" actions:</h2>
 * <ul>
 *     <li>
 *         Excel, editCell
 *     </li>
 *     <li>
 *         Excel, paste
 *     </li>
 *     <li>
 *         Chrome, paste
 *     </li>
 *     <li>
 *         Chrome, editField
 *     </li>
 * </ul>
 * <br>
 * <h2>Redundant cases:</h2>
 * <ul>
 *     <li>
 *         <h3>
 *             Redundant "editCell" action.
 *         </h3>
 *         If there are two "editCell" actions with the same target id
 *         (cell address) and there is any number of actions between them,
 *         except "getCell" action and "copyCell" action that have the same
 *         cell address, the first "editCell" action is redundant.
 *         <br>
 *         Example:
 *         <pre>
 *             <mark style="background-color: #FF7B62">"Excel", "editCell", "C1", "1"</mark>
 *             "Excel", "getCell", "D11", "2"
 *             <mark>"Excel", "editCell", "C1", "2"</mark>
 *         </pre>
 *         <br>
 *         The second action "getCell" has cell address equals to "D11",
 *         when both "editCell" actions have cell address equals to "C1",
 *         it means that the first "editCell" action is redundant.
 *     </li>
 *     <li>
 *         <h3>
 *             Redundant "pasteIntoCell" action.
 *         </h3>
 *         If there are two "pasteIntoCell" actions with the same workbook name,
 *         sheet name and target id (cell address) and any number of actions
 *         between them except "copyCell" action with the same workbook name,
 *         sheet name and cell address, the first "pasteIntoCell" action is
 *         redundant.
 *         <br>
 *         Example:
 *         <pre>
 *             <mark style="background-color: #FF7B62">"Excel", "pasteIntoCell", "Book1", "Sheet1", "A1", "1"</mark>
 *             "Excel", "getCell", "Book1", "Sheet1", "D11", "2"
 *             <mark>"Excel", "pasteIntoCell", "Book1", "Sheet1", "A1", "1"</mark>
 *         </pre>
 *         <br>
 *         The second "pasteIntoCell" action has the same workbook name, sheet name and cell address
 *         and there is no "copyCell" action with the same workbook name, sheet name and cell
 *         address between these two "pasteIntoCell" actions, so the first "pasteIntoCell" action is
 *         redundant.
 *     </li>
 *     <li>
 *         <h3>
 *             Redundant "pasteIntoRange" action.
 *         </h3>
 *         If there are two "pasteIntoRange" actions with the same workbook name,
 *         sheet name and target id (cell range) and any number of actions
 *         between them except "copyRange" action with the same workbook name,
 *         sheet name and cell address, the first "pasteIntoRange" action is
 *         redundant.
 *         <br>
 *         Example:
 *         <pre>
 *             <mark style="background-color: #FF7B62">"Excel", "pasteIntoRange", "Book1", "Sheet1", "B4:F4", "[[1;2;3;4;5]]"</mark>
 *             "Excel", "getCell", "Book1", "Sheet1", "D11", "2"
 *             <mark>"Excel", "pasteIntoRange", "Book1", "Sheet1", "B4:F4", "[[1;2;3;4;5]]"</mark>
 *         </pre>
 *         <br>
 *         The second "pasteIntoRange" action has the same workbook name, sheet name and cell range
 *         and there is no "copyRange" action with the same workbook name, sheet name and cell
 *         range between these two "pasteIntoRange" actions, so the first "pasteIntoRange" action
 *         is redundant.
 *     </li>
 *     <li>
 *         <h3>
 *             Redundant "paste" action.
 *         </h3>
 *         If there are two "paste" actions with the same target name and target value
 *         and any number of actions between them except "copy" action with the same
 *         target name, the first "paste" action is redundant.
 *         <br>
 *         Example:
 *         <pre>
 *         <mark style="background-color: #FF7B62">"Chrome", "paste", "John", "First_Name", "Mary"</mark>
 *         "Excel", "getCell", "Book1", "Sheet1", "D11", "2"
 *         <mark>"Chrome", "paste", "Kate", "First_Name", "Mary"</mark>
 *         </pre>
 *         <br>
 *         The second "paste" action has the same target name ("First_Name") and target value ("Mary")
 *         and there is no "copy" action with the same target name between these two "paste" actions,
 *         so the first "paste" action is redundant.
 *     </li>
 *     <li>
 *         <h3>
 *             Redundant "editField" action.
 *         </h3>
 *         If there are two "editField" actions with the same target name and there is no copy action with
 *         the same target name between them, the first "editField" action is redundant.
 *         <br>
 *         Example:
 *         <pre>
 *             <mark style="background-color: #FF7B62">"Chrome", "editField", "Doe", "First_Name"</mark>
 *             <mark>"Chrome", "editField", "John", "First_Name"</mark>
 *         </pre>
 *         <br>
 *         The second "editField" action has the same target name ("First_Name"), so the first "editField"
 *         action is redundant.
 *     </li>
 *     <li>
 *         <h3>
 *             Redundant "editField" action and associated "paste" actions.
 *         </h3>
 *         "paste" action generates "editField" action, so if there is "paste" action, after which
 *         there is "editField" action and then "editField" action with the same target name and target
 *         value that is not a concatenation of the first "editField" action target value and "paste" action
 *         target value and there is no "copy" action between these two "editField" actions, the first "paste"
 *         action and "editField" action are redundant.
 *         <br>
 *         Example:
 *         <pre>
 *         <mark style="background-color: #FF7B62">"Chrome", "paste", "John", "First_Name", ""</mark>
 *         <mark style="background-color: #FF7B62">"Chrome", "editField", "John", "First_Name"</mark>
 *         "Excel", "getCell", "Book1", "Sheet1", "D11", "2"
 *         <mark>"Chrome", "editField", "Kate", "First_Name"</mark>
 *         </pre>
 *         <br>
 *         The second "editField" action has the same target name ("First_Name") as the first "editField" action,
 *         there is no "copy" with the same target name action between these two "editField" actions and target value
 *         of the second "editField" action ("Kate") is not a result of concatenation of the first "paste" action
 *         target value and the first "editField" target value, so the first "paste" action and the first "editField"
 *         action are redundant.
 *     </li>
 * </ul>
 */
public class WriteSimplifier {

    /**
     * This is a regular expression that corresponds to the case when
     * there is any number of actions except "geCell" action and
     * "copyCell" action between "editCell" action and another
     * "editCell" action with the same target id (cell address).
     */
    private static String redundantEditCellRegex = ".*\"editCell\",(\"([^\"]|\"\")*\",){4}(\"([^\"]|\"\")*\"),.*\\n" +
                                                   "(((\"([^\"]|\"\")*\",){3}((?!(\"getCell\"|\"copyCell\"),(\"([^\"]|\"\")*\",){4}\\3).)*\\n)*" +
                                                   ".*\"editCell\",(\"([^\"]|\"\")*\",){4}\\3,.*\\n*)";

    /**
     * This is a regular expression that corresponds to the case when
     * there are two "pasteIntoCell" actions with the same workbook name,
     * sheet name and target id (cell address) and any number of actions
     * between them except "copyCell" action with the same workbook name,
     * sheet name and cell address.
     */
    private static String redundantPasteIntoCellRegex = ".*\"pasteIntoCell\",(\"([^\"]|\"\")*\",){2}((\"([^\"]|\"\")*\",){3}).*\\n" +
                                                        "(((\"([^\"]|\"\")*\",){3}((?!\"copyCell\",(\"([^\"]|\"\")*\",){2}\\3).)*\\n)*" +
                                                        ".*\"pasteIntoCell\",(\"([^\"]|\"\")*\",){2}\\3.*\\n*)";

    /**
     * This is a regular expression that corresponds to the case when
     * there are two "pasteIntoRange" actions with the same workbook name,
     * sheet name and target id (cell range) and any number of actions
     * between them except "copyRange" action with the same workbook name,
     * sheet name and cell range.
     */
    private static String redundantPasteIntoRangeRegex = ".*\"pasteIntoRange\",(\"([^\"]|\"\")*\",){2}((\"([^\"]|\"\")*\",){3}).*\\n" +
                                                         "(((\"([^\"]|\"\")*\",){3}((?!\"copyRange\",(\"([^\"]|\"\")*\",){2}\\3).)*\\n)*" +
                                                         ".*\"pasteIntoRange\",(\"([^\"]|\"\")*\",){2}\\3.*\\n*)";

    /**
     * This is a regular expression that corresponds to the case when
     * there are two "paste" actions with the same target name and
     * target value and any number of actions between them except
     * "copy" action with the same target name.
     */
    private static String redundantDoublePasteRegex = ".*\"paste\",(\"([^\"]|\"\")*\",)(\"([^\"]|\"\")*\",)(\"([^\"]|\"\")*\",){6}(\"([^\"]|\"\")*\",)(\"([^\"]|\"\")*\",).*\\n" +
                                                      "(((\"([^\"]|\"\")*\",){3}((?!\"copy\",(\"([^\"]|\"\")*\",){8}\\7).)*\\n)*" +
                                                      ".*\"paste\",(\"([^\"]|\"\")*\",){2}(\"([^\"]|\"\")*\",){6}\\7\\9.*\\n*)";

    /**
     * This is a regular expression that corresponds to the case when
     * the is any number of actions between two "editField" actions and
     * the second "editField" action has the same target name as the
     * first "editField" action.
     */
    private static String redundantDoubleEditFieldRegex = "(.*\"editField\",(\"([^\"]|\"\")*\",){8}(\"([^\"]|\"\")*\",)(\"([^\"]|\"\")*\",).*\\n)" +
                                                          "(((\"([^\"]|\"\")*\",){3}((?!\"copy\",(((?!,).)*,){8}\\4).)*\\n)*" +
                                                          ".*\"editField\",(\"([^\"]|\"\")*\",){8}\\4\\6.*\\n*)";

    /**
     * This is a regular expression that corresponds to the case when
     * there is any number of actions except "paste" action then any number
     * of "paste" actions and any number of any actions, then two "editField"
     * actions with any number of action between theme except "copy" action with
     * the same target name. The second "editField" action has the same target
     * name as the first "editField" action and the second "editField" action
     * target value should not contain any target value from the first "editField"
     * action.
     */
    private static String pasteEditFieldWithoutCopyRegex = "((((?!\"paste\").)*\\n)*)" +
                                                           "((.*\"paste\",(\"([^\"]|\"\")*\",){8}(\"([^\"]|\"\")*\"),.*\\n)*)" +
                                                           "(((.*\\n)*)" +
                                                           "(.*\"editField\",(\"([^\"]|\"\")*\",){8}(\"([^\"]|\"\")*\"),\"(([^\"]|\"\")*)\",.*\\n)" +
                                                           "(" +
                                                           "((\"([^\"]|\"\")*\",){3}((?!\"copy\",(\"([^\"]|\"\")*\",){8}\\16).)*\\n)*" +
                                                           ".*\"editField\",(\"([^\"]|\"\")*\",){8}\\16,(((?!\\18).)*),.*\\n*))";

    /**
     * This is a regular expression that corresponds to the case when
     * there are two "editField" actions and any number of "paste" actions
     * between them with the same target name as the first "editField". The
     * second "editField" action has the same target name as the first
     * "editField" action and target value is a concatenation of the first
     * "editField" target value and "paste" action content.
     */
    private static String pasteBetweenEditFieldsRegex = "(.*\"editField\",(\"([^\"]|\"\")*\",){8}(\"([^\"]|\"\")*\",)\"(([^\"]|\"\")*)\",.*\\n)" +
                                                        "(" +
                                                        "((\"([^\"]|\"\")*\",){3}\"paste\",(\"([^\"]|\"\")*\",)\"(([^\"]|\"\")*)\",(\"([^\"]|\"\")*\",){6}\\4.*\\n)*" +
                                                        ".*\"editField\",(\"([^\"]|\"\")*\",){8}\\4\"(\\6\\14)\",.*\\n*)";

    /**
     * Checks if the log contains a pattern that matches {@link WriteSimplifier#redundantEditCellRegex},
     * i.e the log contains two "editCell" actions with the same cell address,
     * and there is any number of action between them except "getCell" action
     * and "copyCell" action with the same cell address.
     *
     * @param   log the log that contains input actions.
     * @return  <code>true</code> if the log contains pattern that
     *          matches {@link WriteSimplifier#redundantEditCellRegex};
     *          <code>false</code> otherwise.
     */
    public static boolean containsRedundantEditCell(String log) {
        Pattern pattern = Pattern.compile(redundantEditCellRegex);
        Matcher matcher = pattern.matcher(log);

        return matcher.find();
    }

    /**
     * Checks if the log contains a pattern that matches {@link WriteSimplifier#redundantPasteIntoCellRegex},
     * i.e the log contains two "pasteIntoCell" actions with the same
     * workbook name, sheet name and target id (cell address) and
     * there is any number of action between them except "copyCell"
     * action with the same workbook name, sheet name and cell address.
     *
     * @param   log the log that contains input actions.
     * @return  <code>true</code> if the log contains pattern that
     *          matches {@link WriteSimplifier#redundantPasteIntoCellRegex};
     *          <code>false</code> otherwise.
     */
    public static boolean containsRedundantPasteIntoCell(String log) {
        Pattern p = Pattern.compile(redundantPasteIntoCellRegex);
        Matcher matcher = p.matcher(log);

        return matcher.find();
    }

    /**
     * Checks if the log contains a pattern that matches {@link WriteSimplifier#redundantPasteIntoRangeRegex},
     * i.e the log contains two "pasteIntoRange" actions with the same
     * workbook name, sheet name and target id (cell range) and
     * there is any number of action between them except "copyRange"
     * action with the same workbook name, sheet name and cell range.
     *
     * @param   log the log that contains input actions.
     * @return  <code>true</code> if the log contains pattern that
     *          matches {@link WriteSimplifier#redundantPasteIntoRangeRegex};
     *          <code>false</code> otherwise.
     */
    public static boolean containsRedundantPasteIntoRange(String log) {
        Pattern p = Pattern.compile(redundantPasteIntoRangeRegex);
        Matcher matcher = p.matcher(log);

        return matcher.find();
    }

    /**
     * Checks if the log contains a pattern that matches {@link WriteSimplifier#redundantDoublePasteRegex},
     * i.e the log contains two "paste" actions with the same
     * target name and target value and there is any number of
     * action between them except "copy" action with the same
     * target name.
     *
     * @param   log the log that contains input actions.
     * @return  <code>true</code> if the log contains pattern that
     *          matches {@link WriteSimplifier#redundantDoublePasteRegex};
     *          <code>false</code> otherwise.
     */
    public static boolean containsRedundantDoublePaste(String log) {
        Pattern p = Pattern.compile(redundantDoublePasteRegex);
        Matcher matcher = p.matcher(log);

        return matcher.find();
    }

    /**
     * Checks if the log contains a pattern that matches {@link WriteSimplifier#redundantDoubleEditFieldRegex},
     * i.e the log contains two "editField" actions and the second "editField" action has
     * the same target name as the first "editField" action.
     *
     * @param   log the log that contains input actions.
     * @return  <code>true</code> if the log contains pattern that
     *          matches {@link WriteSimplifier#redundantDoubleEditFieldRegex};
     *          <code>false</code> otherwise.
     */
    public static boolean containsRedundantDoubleEditField(String log) {
        Pattern p = Pattern.compile(redundantDoubleEditFieldRegex);
        Matcher matcher = p.matcher(log);

        return matcher.find();
    }

    /**
     * Checks if the log contains a pattern that matches {@link WriteSimplifier#pasteEditFieldWithoutCopyRegex}
     * and does not contain a pattern that matches {@link WriteSimplifier#pasteBetweenEditFieldsRegex}.
     *
     * @param   log the log that contains input actions.
     * @return  <code>true</code> if the log contains a pattern that matches
     *          {@link WriteSimplifier#redundantDoubleEditFieldRegex} and does not
     *          contain a pattern that matches {@link WriteSimplifier#pasteBetweenEditFieldsRegex}.
     *          <code>false</code> otherwise.
     */
    public static boolean containsRedundantEditField(String log) {
        Pattern withoutCopyPattern = Pattern.compile(pasteEditFieldWithoutCopyRegex);
        Pattern pateBetweenEditFieldsPattern = Pattern.compile(pasteBetweenEditFieldsRegex);

        return withoutCopyPattern.matcher(log).find() &&
                !pateBetweenEditFieldsPattern.matcher(log).find();
    }

    /**
     * Removes all redundant "editCell" actions from the log.
     * <p>
     * If the log contains pattern that matches {@link WriteSimplifier#redundantEditCellRegex},
     * the method will remove first "editCell" action in the pattern. The method will be called
     * again if the log contains redundant "editCell" action after replacing the pattern that
     * matches {@link WriteSimplifier#redundantEditCellRegex} until there are none of them.
     * </p>
     *
     * @param log   the log that contains input actions.
     * @return      the log without redundant "editCell" actions.
     */
    public static String removeRedundantEditCell(String log) {
        /*
            $5 is a parameter of WriteSimplifier#redundantEditCellRegex that
            represents every action after the first "editCell" action and
            the second "editCell" action in the pattern.
         */
        log = log.replaceAll(redundantEditCellRegex, "$5");

        if (containsRedundantEditCell(log)) {
            return removeRedundantEditCell(log);
        }

        return log;
    }

    /**
     * Removes all redundant "pasteIntoCell" actions from the log.
     * <p>
     * If the log contains pattern that matches {@link WriteSimplifier#redundantPasteIntoCellRegex},
     * the method will remove first "pasteIntoCell" action in the pattern. The method will be called
     * again if the log contains redundant "pasteIntoCell" action after replacing the pattern that
     * matches {@link WriteSimplifier#redundantPasteIntoCellRegex} until there are none of them.
     * </p>
     *
     * @param log   the log that contains input actions.
     * @return      the log without redundant "pasteIntoCell" actions.
     */
    public static String removeRedundantPasteIntoCell(String log) {
        /*
            $6 is a parameter of WriteSimplifier#redundantPasteIntoCellRegex that
            represents every action after the first "pasteIntoCell" action
            and the second "pasteIntoCell" action in the pattern.
         */
        log = log.replaceAll(redundantPasteIntoCellRegex, "$6");

        if (containsRedundantPasteIntoCell(log)) {
            return removeRedundantPasteIntoCell(log);
        }

        return log;
    }

    /**
     * Removes all redundant "pasteIntoRange" actions from the log.
     * <p>
     * If the log contains pattern that matches {@link WriteSimplifier#redundantPasteIntoRangeRegex},
     * the method will remove first "pasteIntoRange" action in the pattern. The method will be called
     * again if the log contains redundant "pasteIntoRange" action after replacing the pattern that
     * matches {@link WriteSimplifier#redundantPasteIntoRangeRegex} until there are none of them.
     * </p>
     *
     * @param log   the log that contains input actions.
     * @return      the log without redundant "pasteIntoRange" actions.
     */
    public static String removeRedundantPasteIntoRange(String log) {
        /*
            $6 is a parameter of WriteSimplifier#redundantPasteIntoRangeRegex that
            represents every action after the first "pasteIntoRange" action
            and the second "pasteIntoRange" action in the pattern.
         */
        log = log.replaceAll(redundantPasteIntoRangeRegex, "$6");

        if (containsRedundantPasteIntoRange(log)) {
            return removeRedundantPasteIntoRange(log);
        }

        return log;
    }

    /**
     * Removes all redundant "paste" actions from the log.
     * <p>
     * If the log contains pattern that matches {@link WriteSimplifier#redundantDoublePasteRegex},
     * the method will remove first "paste" action in the pattern. The method will be called
     * again if the log contains redundant "paste" action after replacing the pattern that
     * matches {@link WriteSimplifier#redundantDoublePasteRegex} until there are none of them.
     * </p>
     *
     * @param log   the log that contains input actions.
     * @return      the log without redundant "paste" actions.
     */
    public static String removeRedundantDoublePaste(String log) {
        /*
            $11 is a parameter of WriteSimplifier#redundantPasteRegex that
            represents every action after the first "paste" action
            and the second "paste" action in the pattern.
         */
        log = log.replaceAll(redundantDoublePasteRegex, "$11");

        if (containsRedundantDoublePaste(log)) {
            return removeRedundantDoublePaste(log);
        }

        return log;
    }

    /**
     * Removes the first "editField" action from double "editField" actions from the log.
     * <p>
     * If the log contains pattern that matches {@link WriteSimplifier#redundantDoubleEditFieldRegex},
     * the method will remove first "editField" action in the pattern. The method will be called
     * again if the log contains double "editFiled" actions after replacing the pattern that
     * matches {@link WriteSimplifier#redundantDoubleEditFieldRegex} until there are none of them.
     * </p>
     *
     * @param log   the log that contains input actions.
     * @return      the log without duplicated "editField" actions.
     */
    public static String removeRedundantDoubleEditField(String log) {
        /*
            $8 is a parameter of WriteSimplifier#redundantDoubleEditFieldRegex that
            represents the second "editField" action.
         */
        log = log.replaceAll(redundantDoubleEditFieldRegex, "$8");

        if (containsRedundantDoubleEditField(log)) {
            return removeRedundantDoubleEditField(log);
        }

        return log;
    }

    /**
     * Removes all redundant "editField" actions and associated "paste" actions from the log.
     * <p>
     * If the log contains a pattern that matches {@link WriteSimplifier#pasteEditFieldWithoutCopyRegex}
     * and does not contains a pattern that matches {@link WriteSimplifier#pasteBetweenEditFieldsRegex},
     * the method will check if the the log contains the first "paste" action and this action target name and
     * the first "editField" action target name are equal (both action from the pattern in the log that matches
     * {@link WriteSimplifier#pasteEditFieldWithoutCopyRegex}), if so, the method will remove the first
     * "paste" action from that part of the log that matches {@link WriteSimplifier#pasteEditFieldWithoutCopyRegex}.
     * If the pattern does not contain "paste" action or the first "paste" action target name and the first "editField"
     * action target name are not equal, the method will remove the first "paste" action (if presents int the pattern)
     * and the first "editField" action from the pattern in the log that matches {@link WriteSimplifier#pasteEditFieldWithoutCopyRegex}.
     * Then, if the log contains a pattern that matches {@link WriteSimplifier#pasteBetweenEditFieldsRegex}, the method
     * will remove the first "editField" action from the pattern in the log that matches {@link WriteSimplifier#pasteBetweenEditFieldsRegex}.
     * </p>
     *
     * @param log   the log that contains input actions.
     * @return      the log without redundant "paste" actions and associated "editField" actions.
     */
    public static String removeRedundantEditField(String log) {
        Pattern withoutCopyPattern = Pattern.compile(pasteEditFieldWithoutCopyRegex);
        Matcher withoutCopyMatcher = withoutCopyPattern.matcher(log);

//        Pattern pastePattern = Pattern.compile(pasteBetweenEditFieldsRegex);
//        Matcher pasteMatcher = pastePattern.matcher(log);
        /*
            group(8)    represents target name of the first "paste" action.
            group(16)   represents target name of the first "editField" action.
            group(1)    represents every action before the first "paste" action.
            group(10)   represents every action after the first "paste" action.
            group(11)   represents every action between the first "paste" action and
                        the first "editField" action.
            group(20)   represents every action after the first "editField" action.
         */
//        if (withoutCopyMatcher.find() && !pasteMatcher.find()) {
        if (withoutCopyMatcher.find()) {
            log = withoutCopyMatcher.replaceAll(mr -> {
                if (mr.group(8) != null &&
                        mr.group(16) != null &&
                        mr.group(8).equals(mr.group(16))) {
                    return mr.group(1) + mr.group(10);
                }
                return mr.group(1) + mr.group(4) + mr.group(11) + mr.group(20);
            });

            // $8 represents everything after the first "editField" action.
            log = log.replaceAll(pasteBetweenEditFieldsRegex, "$8");
            return removeRedundantEditField(log);
        }

        return log;
    }
}

package com.simplifier.validation;

import java.util.Arrays;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * This class consists of methods that operate on log:
 * check if log contains non-valid action, and if so,
 * throw an exception.
 */
public class Validator {

    /**
     * Checks if on of these actions: editField, copy, copyCell,
     * copyRange, paste, pasteIntoCell, editCell, editRange, getCell
     * does not have target id (if target application is Excel) or
     * target name (if target application is Chrome), and if so,
     * throws an IllegalArgumentException exception.
     *
     * @param log   the log that contains input actions.
     */
    public static void validateForIdOrName(String log) {
        String actionRegex = "(\"([^\"]|\"\")*\",){2}(\"Chrome\"|\"Excel\"),(\"editField\"|\"copy\"|\"copyCell\"|" +
                             "\"copyRange\"|\"paste\"|\"pasteIntoCell\"|\"pasteIntoRange\"|\"editCell\"|" +
                             "\"editRange\"|\"getCell\").*";

        String[] actions = log.split("\n");

        // Filter array of actions: return actions that matches actionRegex and check if any of these actions
        // has non-valid target id or target name.
        Arrays.stream(actions)
                .filter(action -> Pattern.compile(actionRegex).matcher(action).matches())
                .forEach(Validator::checkActionForValidIdOrName);
    }

    private static void checkActionForValidIdOrName(String action) {
        String regexId = "(\"([^\"]|\"\")*\",){8}(\"([^\"]|\"\")+\",).*";
        String regexName = "(\"([^\"]|\"\")*\",){12}(\"([^\"]|\"\")+\",).*";

        Pattern patternId = Pattern.compile(regexId);
        Matcher matcherId = patternId.matcher(action);

        Pattern patternName = Pattern.compile(regexName);
        Matcher matcherName = patternName.matcher(action);

        if (!matcherId.matches() && !matcherName.matches()) {
            throw new IllegalArgumentException("Target id or name was missed");
        }
    }
}

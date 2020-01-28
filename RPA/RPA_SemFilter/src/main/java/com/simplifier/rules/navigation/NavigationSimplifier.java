package com.simplifier.rules.navigation;

import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * This class consists of methods that operate on log:
 * check if log contains redundant navigation action, and if so,
 * remove them and return new log.
 * List of "Navigation" actions:
 * <ul>
 *     <li>
 *         ClickTextField
 *         <br>
 *         Any "clickTextField" action is redundant.
 *     </li>
 * </ul>
 */
public class NavigationSimplifier {

    /**
     * This is regular expression that corresponds to the case when
     * there is "clickTextField" action.
     */
    private static String redundantClickTextFieldRegex = "((\"([^\"]|\"\")*\",){3}\"clickTextField\",.*\\n*)";

    /**
     * This method is used to check if the log contains a
     * pattern that matches {@link NavigationSimplifier#redundantClickTextFieldRegex},
     * i.e the log contains "clickTextField" actions.
     * <p>
     *
     * @param   log the log that contains input actions.
     * @return  <code>true</code> if the log contains pattern that
     *          matches {@link NavigationSimplifier#redundantClickTextFieldRegex};
     *          <code>false</code> otherwise.
     */
    public static boolean containsRedundantClickTextField(String log) {
        Pattern pattern = Pattern.compile(redundantClickTextFieldRegex);
        Matcher matcher = pattern.matcher(log);

        return matcher.find();
    }

    /**
     * This method is used to remove all redundant "clickTextField" actions
     * from the log.
     * <p>
     * If the log contains pattern that matches {@link NavigationSimplifier#redundantClickTextFieldRegex},
     * the method will remove "clickTextField" action in the pattern.
     * </p>
     *
     * @param log   the log that contains input actions.
     * @return      the log without redundant "clickTextField" actions.
     */
    public static String removeRedundantClickTextField(String log) {
        if (containsRedundantClickTextField(log)) {
            log = log.replaceAll(redundantClickTextFieldRegex, "");
            return removeRedundantClickTextField(log);
        }

        return log;
    }
}

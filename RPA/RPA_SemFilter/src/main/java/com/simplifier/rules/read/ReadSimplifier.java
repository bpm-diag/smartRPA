package com.simplifier.rules.read;

import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * This class consists of methods that operate on the log:
 * check if log contains redundant read action, and if so,
 * remove them and return a new log.
 * <br><br>
 * List of "Read" actions:
 * <ul>
 *     <li>
 *         Chrome, copy
 *     </li>
 *     <li>
 *         Excel, copyCell
 *     </li>
 *     <li>
 *         Excel, copyRange
 *     </li>
 * </ul>
 * <br>
 * Redundant cases:
 * <ul>
 *     <li>
 *         If there is any number of actions between two "copy" actions
 *         except "paste" action, the first "copy" action is redundant.
 *         The case is described by {@link ReadSimplifier#redundantFirstCopyRegex}.
 *         <br>
 *         Example:
 *         <pre>
 *             <mark style="background-color: #FF7B62">"Chrome", "copy", "text"</mark>
 *             "Chrome", "editField", "text"
 *             "Chrome", "editField", "text"
 *             <mark>"Chrome", "copy", "text"</mark>
 *         </pre>
 *         First "copy" action is redundant.
 *         <br><br>
 *     </li>
 *     <li>
 *         If the log contains a single "copy" action and there is no "paste"
 *         action after it, the "copy" action is redundant.
 *         The case is described by {@link ReadSimplifier#singleCopyRegex}.
 *         <br>
 *         Example:
 *         <pre>
 *             <mark style="background-color: #FF7B62">"Chrome", "copy", "text"</mark>
 *             "Chrome", "editField", "text"
 *             "Chrome", "editField", "text"
 *         </pre>
 *         "copy" action is redundant.
 *         <br><br>
 *     </li>
 * </ul>
 */
public class ReadSimplifier {

    /**
     * This is regular expression that corresponds to the case when
     * there is any number of actions except "paste" action
     * between two "copy" actions.
     */
    private static String redundantFirstCopyRegex = "((\"([^\"]|\"\")*\",){3}\"copy.*\\n)" +
                                                    "((((?!(\"([^\"]|\"\")*\",){3}\"paste).)*\",.*\\n)*" +
                                                    "(\"([^\"]|\"\")*\",){3}\"copy.*\\n*)";

    /**
     * This is a regular expression that corresponds to the case when
     * the log contains a single "copy" action and there is no paste
     * action after it.
     */
    private static String singleCopyRegex = "((.*\\n)*)" +
                                            "((\"([^\"]|\"\")*\",){3}(\"copy[a-zA-Z]*\",)(\"([^\"]|\"\")*\",)(\"([^\"]|\"\")*\",).*\\n*)" +
                                            "(((\"([^\"]|\"\")*\",){3}(?!((\"paste[a-zA-Z]*\",(\"([^\"]|\"\")*\",)\\9)|\"copy[a-zA-Z]*\")).*\\n*)*)";

    /**
     * This method is used to check if the log contains a
     * pattern that matches {@link ReadSimplifier#redundantFirstCopyRegex},
     * i.e the log contains two "copy" actions, and there is any number of action
     * between them except "paste" action.
     * <p>
     * The method checks if the log contains a pattern that contains
     * any number of actions except "paste" action between two "copy"
     * actions.
     * </p>
     *
     * @param   log the log that contains input actions.
     * @return  <code>true</code> if the log contains pattern that
     *          matches {@link ReadSimplifier#redundantFirstCopyRegex};
     *          <code>false</code> otherwise.
     */
    public static boolean containsRedundantCopy(String log) {
        Pattern p = Pattern.compile(redundantFirstCopyRegex);
        Matcher matcher = p.matcher(log);

        return matcher.find();
    }

    /**
     * This method is used to check if the log contains a
     * pattern that matches {@link ReadSimplifier#singleCopyRegex},
     * i.e the log contains a single "copy" action and there is no "paste"
     * action after it.
     * <p>
     * The method checks if the log contains a pattern that contains a
     * single "copy" action and there is no "paste" action after it.
     * </p>
     *
     * @param   log the log that contains input actions.
     * @return  <code>true</code> if the log matches {@link ReadSimplifier#singleCopyRegex}.
     *          <code>false</code> otherwise.
     */
    public static boolean containsSingleCopy(String log) {
        Pattern p = Pattern.compile(singleCopyRegex);
        Matcher matcher = p.matcher(log);

        return matcher.matches();
    }

    /**
     * This method is used to remove all redundant copy actions
     * from the log.
     * <p>
     * If the log contains pattern that matches {@link ReadSimplifier#redundantFirstCopyRegex},
     * the method will remove first "copy" action in the pattern. The method will be called again
     * if the log contains redundant "copy" action after replacing the pattern that matches
     * {@link ReadSimplifier#redundantFirstCopyRegex} until there are none of them.
     * </p>
     *
     * @param log   the log that contains input actions.
     * @return      the log without redundant "copy" actions.
     */
    public static String removeRedundantCopy(String log) {
        if (containsRedundantCopy(log)) {
            /*
                $4 is a parameter of ReadSimplifier#redundantFirstCopyRegex that
                is responsible for every action after the first "copy" action and
                the second "copy" action in the pattern.
             */
            log = log.replaceAll(redundantFirstCopyRegex, "$4");
            return removeRedundantCopy(log);
        }

        return log;
    }

    /**
     * This method is used to remove all single "copy" actions
     * from the log.
     * <p>
     * If the log contains pattern that matches {@link ReadSimplifier#singleCopyRegex},
     * the method will remove single "copy" action from the log.
     * </p>
     *
     * @param   log the log that contains input actions.
     * @return  the log without single "copy" action.
     */
    public static String removeSingleCopy(String log) {
        if (containsSingleCopy(log)) {
            /*
                $1 is a parameter of ReadSimplifier#singleCopyRegex
                that represents every action before single "copy"
                action. $7 is a parameter of ReadSimplifier#singleCopyRegex
                that represents every action after a single "copy" action.
            */
            log = log.replaceAll(singleCopyRegex, "$1$11");
            return removeSingleCopy(log);
        }

        return log;
    }
}

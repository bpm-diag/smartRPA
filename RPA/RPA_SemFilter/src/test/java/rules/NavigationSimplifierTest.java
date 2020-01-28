package rules;

import com.simplifier.rules.navigation.NavigationSimplifier;
import org.junit.Test;

import static org.hamcrest.core.Is.is;
import static org.hamcrest.core.IsEqual.equalTo;
import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertThat;


public class NavigationSimplifierTest {

    @Test
    public void testDeleteRedundantClickTextField() {
        String logs = "2019-04-02T17:51:41.579Z,st,Excel,getCell,,,excel.xlsx,Sheet1,A1,,,,,[[3]],,,,\n" +
                "2019-04-02T17:51:44.697Z,st,Chrome,clickTextField,,,,,,,INPUT,text,SingleLine,,,,,\n" +
                "2019-04-02T17:53:41.579Z,st,Excel,getCell,,,excel.xlsx,Sheet1,A2,,,,,[[3]],,,,\n";

        assertThat(NavigationSimplifier.containsRedundantClickTextField(logs), is(equalTo(true)));

        assertEquals(NavigationSimplifier.removeRedundantClickTextField(logs),
                "2019-04-02T17:51:41.579Z,st,Excel,getCell,,,excel.xlsx,Sheet1,A1,,,,,[[3]],,,,\n" +
                        "2019-04-02T17:53:41.579Z,st,Excel,getCell,,,excel.xlsx,Sheet1,A2,,,,,[[3]],,,,\n");
    }
}

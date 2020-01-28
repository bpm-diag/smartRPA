package rules;

import com.simplifier.rules.read.ReadSimplifier;
import org.junit.Test;

import static org.hamcrest.core.Is.is;
import static org.hamcrest.core.IsEqual.equalTo;
import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertThat;


public class ReadSimplifierTest {

    @Test
    public void testDeleteRedundantCopy() {
        String logs = "2019-04-02T17:56:41.899Z,st,Excel,copyCell,,3,excel.xlsx,Sheet1,A1,,,,,[[3]]\n" +
                "2019-04-02T17:56:41.578Z,st,Excel,getCell,,,excel.xlsx,Sheet1,C1,,,,,[[3]],,,,\n" +
                "2019-04-02T17:56:47.899Z,st,Excel,copyCell,,3,excel.xlsx,Sheet1,B1,,,,,[[3]]\n" +
                "2019-04-03T06:28:26.289Z,st,Chrome,editField,,,,,Date-date,,INPUT,text,date,17-10-2019,,,,\n";

        assertThat(ReadSimplifier.containsRedundantCopy(logs), is(equalTo(true)));

        assertEquals(ReadSimplifier.removeRedundantCopy(logs),
                "2019-04-02T17:56:41.578Z,st,Excel,getCell,,,excel.xlsx,Sheet1,C1,,,,,[[3]],,,,\n" +
                        "2019-04-02T17:56:47.899Z,st,Excel,copyCell,,3,excel.xlsx,Sheet1,B1,,,,,[[3]]\n" +
                        "2019-04-03T06:28:26.289Z,st,Chrome,editField,,,,,Date-date,,INPUT,text,date,17-10-2019,,,,\n");
    }

    @Test
    public void testPasteBetweenTwoCopy() {
        String logs = "2019-04-02T17:56:41.899Z,st,Excel,copyCell,,3,excel.xlsx,Sheet1,A1,,,,,[[3]]\n" +
                "2019-04-02T17:56:41.578Z,st,Excel,getCell,,,excel.xlsx,Sheet1,C1,,,,,[[3]],,,,\n" +
                "2019-04-02T17:56:44.946Z,st,Chrome,paste,,3,,,,,INPUT,text,SingleLine,,,,,\n" +
                "2019-04-02T17:56:47.899Z,st,Excel,copyCell,,3,excel.xlsx,Sheet1,B1,,,,,[[3]]\n" +
                "2019-04-02T17:56:40.656Z,st,Chrome,editField,,,,,,,INPUT,text,SingleLine,\n";

        assertThat(ReadSimplifier.containsRedundantCopy(logs), is(equalTo(false)));

        assertEquals(ReadSimplifier.removeRedundantCopy(logs), logs);
    }

    @Test
    public void testDeleteSingleCopy() {
        String logs = "2019-04-02T17:56:41.578Z,st,Excel,getCell,,,excel.xlsx,Sheet1,C1,,,,,[[3]],,,,\n" +
                "2019-04-02T17:56:47.899Z,st,Excel,copyCell,,3,excel.xlsx,Sheet1,B1,,,,,[[3]]\n" +
                "2019-04-03T06:28:26.289Z,st,Chrome,editField,,,,,Date-date,,INPUT,text,date,17-10-2019,,,,\n";

        assertThat(ReadSimplifier.containsSingleCopy(logs), is(equalTo(true)));

        assertEquals(ReadSimplifier.removeSingleCopy(logs),
                "2019-04-02T17:56:41.578Z,st,Excel,getCell,,,excel.xlsx,Sheet1,C1,,,,,[[3]],,,,\n" +
                        "2019-04-03T06:28:26.289Z,st,Chrome,editField,,,,,Date-date,,INPUT,text,date,17-10-2019,,,,\n");
    }

    @Test
    public void testNoSingleCopy() {
        String logs = "2019-04-02T17:56:41.578Z,st,Excel,getCell,,,excel.xlsx,Sheet1,C1,,,,,[[3]],,,,\n" +
                "2019-04-02T17:56:47.899Z,st,Excel,copyCell,,3,excel.xlsx,Sheet1,B1,,,,,[[3]]\n" +
                "2019-04-03T06:28:26.289Z,st,Chrome,editField,,,,,Date-date,,INPUT,text,date,17-10-2019,,,,\n" +
                "2019-04-02T17:56:47.899Z,st,Excel,copyCell,,3,excel.xlsx,Sheet1,C1,,,,,[[3]]\n";

        assertThat(ReadSimplifier.containsSingleCopy(logs), is(equalTo(false)));

        assertEquals(ReadSimplifier.removeSingleCopy(logs), logs);
    }

    @Test
    public void testPasteAfterSingleCopy() {
        String logs = "2019-04-02T17:56:41.578Z,st,Excel,getCell,,,excel.xlsx,Sheet1,C1,,,,,[[3]],,,,\n" +
                "2019-04-03T06:28:26.289Z,st,Chrome,editField,,,,,Date-date,,INPUT,text,date,17-10-2019,,,,\n" +
                "2019-04-02T17:56:47.899Z,st,Excel,copyCell,,3,excel.xlsx,Sheet1,C1,,,,,[[3]]\n" +
                "2019-04-02T17:56:44.946Z,st,Chrome,paste,,3,,,,,INPUT,text,SingleLine,,,,,\n";

        assertThat(ReadSimplifier.containsSingleCopy(logs), is(equalTo(false)));

        assertEquals(ReadSimplifier.removeSingleCopy(logs), logs);
    }
}

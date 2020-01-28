package rules;

import com.simplifier.rules.write.WriteSimplifier;
import org.junit.Test;

import static org.hamcrest.core.Is.is;
import static org.hamcrest.core.IsEqual.equalTo;
import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertThat;

public class WriteSimplifierTest {

    @Test
    public void testDeleteRedundantEditCell() {
        String logs = "2019-04-09T15:15:45.862Z,st,Excel,getRange,,,test.xlsx,Sheet1,A1:F1,,,,,[[1,2,3,4,5,6]],,,,\n" +
                "2019-04-09T15:15:37.970Z,st,Excel,editCell,,,test.xlsx,Sheet1,B1,,,,,2,,,,\n" +
                "2019-04-09T17:58:57.292Z,st,Chrome,editField,,,,,,,INPUT,text,Name_First,test,,,,\n" +
                "2019-04-09T17:58:57.409Z,st,Chrome,clickTextField,,,,,,,INPUT,text,Name_Last,,,,,\n" +
                "2019-04-09T17:58:59.057Z,st,Chrome,editField,,,,,,,INPUT,text,Name_Last,world,,,,\n" +
                "2019-04-09T15:15:37.970Z,st,Excel,editCell,,,test.xlsx,Sheet1,B1,,,,,10,,,,\n";

        assertThat(WriteSimplifier.containsRedundantEditCell(logs), is(equalTo(true)));

        assertEquals("2019-04-09T15:15:45.862Z,st,Excel,getRange,,,test.xlsx,Sheet1,A1:F1,,,,,[[1,2,3,4,5,6]],,,,\n" +
                        "2019-04-09T17:58:57.292Z,st,Chrome,editField,,,,,,,INPUT,text,Name_First,test,,,,\n" +
                        "2019-04-09T17:58:57.409Z,st,Chrome,clickTextField,,,,,,,INPUT,text,Name_Last,,,,,\n" +
                        "2019-04-09T17:58:59.057Z,st,Chrome,editField,,,,,,,INPUT,text,Name_Last,world,,,,\n" +
                        "2019-04-09T15:15:37.970Z,st,Excel,editCell,,,test.xlsx,Sheet1,B1,,,,,10,,,,\n",
                WriteSimplifier.removeRedundantEditCell(logs));
    }

    @Test
    public void testGetCellBetweenTwoEditCell() {
        String logs = "2019-04-09T15:15:45.862Z,st,Excel,getRange,,,test.xlsx,Sheet1,A1:F1,,,,,[[1,2,3,4,5,6]],,,,\n" +
                "2019-04-09T15:15:37.970Z,st,Excel,editCell,,,test.xlsx,Sheet1,B1,,,,,2,,,,\n" +
                "2019-04-09T17:58:57.292Z,st,Chrome,editField,,,,,,,INPUT,text,Name_First,test,,,,\n" +
                "2019-04-09T17:58:57.409Z,st,Chrome,clickTextField,,,,,,,INPUT,text,Name_Last,,,,,\n" +
                "2019-04-09T17:58:59.057Z,st,Chrome,editField,,,,,,,INPUT,text,Name_Last,world,,,,\n" +
                "2019-04-09T15:15:40.051Z,st,Excel,getCell,,,test.xlsx,Sheet1,B1,,,,,2,,,,\n" +
                "2019-04-09T15:15:37.970Z,st,Excel,editCell,,,test.xlsx,Sheet1,B1,,,,,10,,,,\n";

        assertThat(WriteSimplifier.containsRedundantEditCell(logs), is(equalTo(false)));

        assertEquals("2019-04-09T15:15:45.862Z,st,Excel,getRange,,,test.xlsx,Sheet1,A1:F1,,,,,[[1,2,3,4,5,6]],,,,\n" +
                        "2019-04-09T15:15:37.970Z,st,Excel,editCell,,,test.xlsx,Sheet1,B1,,,,,2,,,,\n" +
                        "2019-04-09T17:58:57.292Z,st,Chrome,editField,,,,,,,INPUT,text,Name_First,test,,,,\n" +
                        "2019-04-09T17:58:57.409Z,st,Chrome,clickTextField,,,,,,,INPUT,text,Name_Last,,,,,\n" +
                        "2019-04-09T17:58:59.057Z,st,Chrome,editField,,,,,,,INPUT,text,Name_Last,world,,,,\n" +
                        "2019-04-09T15:15:40.051Z,st,Excel,getCell,,,test.xlsx,Sheet1,B1,,,,,2,,,,\n" +
                        "2019-04-09T15:15:37.970Z,st,Excel,editCell,,,test.xlsx,Sheet1,B1,,,,,10,,,,\n",
                WriteSimplifier.removeRedundantEditCell(logs));
    }

    @Test
    public void testCopyCellBetweenTwoEditCell() {
        String logs = "2019-04-09T15:15:45.862Z,st,Excel,getRange,,,test.xlsx,Sheet1,A1:F1,,,,,[[1,2,3,4,5,6]],,,,\n" +
                "2019-04-09T15:15:37.970Z,st,Excel,editCell,,,test.xlsx,Sheet1,B1,,,,,2,,,,\n" +
                "2019-04-09T17:58:57.292Z,st,Chrome,editField,,,,,,,INPUT,text,Name_First,test,,,,\n" +
                "2019-04-09T17:58:57.409Z,st,Chrome,clickTextField,,,,,,,INPUT,text,Name_Last,,,,,\n" +
                "2019-04-09T17:58:59.057Z,st,Chrome,editField,,,,,,,INPUT,text,Name_Last,world,,,,\n" +
                "2019-04-02T17:56:47.899Z,st,Excel,copyCell,,3,test.xlsx,Sheet1,B1,,,,,2\n" +
                "2019-04-09T15:15:37.970Z,st,Excel,editCell,,,test.xlsx,Sheet1,B1,,,,,10,,,,\n";

        assertThat(WriteSimplifier.containsRedundantEditCell(logs), is(equalTo(false)));

        assertEquals("2019-04-09T15:15:45.862Z,st,Excel,getRange,,,test.xlsx,Sheet1,A1:F1,,,,,[[1,2,3,4,5,6]],,,,\n" +
                        "2019-04-09T15:15:37.970Z,st,Excel,editCell,,,test.xlsx,Sheet1,B1,,,,,2,,,,\n" +
                        "2019-04-09T17:58:57.292Z,st,Chrome,editField,,,,,,,INPUT,text,Name_First,test,,,,\n" +
                        "2019-04-09T17:58:57.409Z,st,Chrome,clickTextField,,,,,,,INPUT,text,Name_Last,,,,,\n" +
                        "2019-04-09T17:58:59.057Z,st,Chrome,editField,,,,,,,INPUT,text,Name_Last,world,,,,\n" +
                        "2019-04-02T17:56:47.899Z,st,Excel,copyCell,,3,test.xlsx,Sheet1,B1,,,,,2\n" +
                        "2019-04-09T15:15:37.970Z,st,Excel,editCell,,,test.xlsx,Sheet1,B1,,,,,10,,,,\n",
                WriteSimplifier.removeRedundantEditCell(logs));
    }

    @Test
    public void testDeleteRedundantChromePaste() {
        String logs = "2019-04-09T20:48:11.819Z,st,Chrome,copy,,hello,,,,,INPUT,text,Name_First,hello,,,,\n" +
                "2019-04-09T20:48:12.848Z,st,Chrome,paste,,hello,,,,,INPUT,text,Name_Last,hello,,,,\n" +
                "2019-04-09T20:48:18.408Z,st,Excel,copyCell,,hello,test.xlsx,Sheet1,F1,,,,,[[6]],,,,\n" +
                "2019-04-09T20:48:19.192Z,st,Chrome,paste,,hello,,,,,INPUT,text,Name_Last,hello,,,,\n";

        assertThat(WriteSimplifier.containsRedundantDoublePaste(logs), is(equalTo(true)));

        assertEquals("2019-04-09T20:48:11.819Z,st,Chrome,copy,,hello,,,,,INPUT,text,Name_First,hello,,,,\n" +
                        "2019-04-09T20:48:18.408Z,st,Excel,copyCell,,hello,test.xlsx,Sheet1,F1,,,,,[[6]],,,,\n" +
                        "2019-04-09T20:48:19.192Z,st,Chrome,paste,,hello,,,,,INPUT,text,Name_Last,hello,,,,\n",
                WriteSimplifier.removeRedundantDoublePaste(logs));
    }

    @Test
    public void testCopyFieldBetweenTwoChromePaste() {
        String logs = "2019-04-09T20:48:11.819Z,st,Chrome,copy,,hello,,,,,INPUT,text,Name_First,hello,,,,\n" +
                "2019-04-09T20:48:12.848Z,st,Chrome,paste,,hello,,,,,INPUT,text,Name_Last,hello,,,,\n" +
                "2019-04-09T20:48:11.819Z,st,Chrome,copy,,hello,,,,,INPUT,text,Name_Last,hello,,,,\n" +
                "2019-04-09T20:48:19.192Z,st,Chrome,paste,,hello,,,,,INPUT,text,Name_Last,hello,,,,\n";

        assertThat(WriteSimplifier.containsRedundantDoublePaste(logs), is(equalTo(false)));

        assertEquals(WriteSimplifier.removeRedundantDoublePaste(logs), logs);
    }

    @Test
    public void testDeleteRedundantChromeEditField() {
        String logs = "2019-04-09T20:48:19.192Z,st,Chrome,paste,,6,,,,,INPUT,text,Name_Last,hello,,,,\n" +
                "2019-04-09T20:48:19.963Z,st,Chrome,editField,,,,,,,INPUT,text,Name_Last,hello world,,,,\n" +
                "2019-04-09T20:48:19.964Z,st,Chrome,editField,,,,,,,INPUT,text,Name_Last,hello,,,,\n";

        assertThat(WriteSimplifier.containsRedundantEditField(logs), is(equalTo(true)));

        assertEquals("2019-04-09T20:48:19.964Z,st,Chrome,editField,,,,,,,INPUT,text,Name_Last,hello,,,,\n",
                WriteSimplifier.removeRedundantEditField(logs));
    }

    @Test
    public void testCopyFieldBetweenTwoChromeEditField() {
        String logs = "2019-04-09T20:48:19.192Z,st,Chrome,paste,,6,,,,,INPUT,text,Name_Last,hello,,,,\n" +
                "2019-04-09T20:48:19.963Z,st,Chrome,editField,,,,,,,INPUT,text,Name_Last,hello world,,,,\n" +
                "2019-04-09T20:48:11.819Z,st,Chrome,copy,,hello world,,,,,INPUT,text,Name_Last,hello world,,,,\n" +
                "2019-04-09T20:48:19.964Z,st,Chrome,editField,,,,,,,INPUT,text,Name_Last,hello,,,,\n";

        assertThat(WriteSimplifier.containsRedundantEditField(logs), is(equalTo(false)));

        assertEquals(WriteSimplifier.removeRedundantEditField(logs), logs);
    }

    @Test
    public void testDeleteConnectedPostToEditField() {
        String logs = "2019-04-29T16:51:37.879Z,st,Chrome,paste,,TEST,,,,,INPUT,text,Name_First,,,,,\n" +
                "2019-04-29T16:51:40.211Z,st,Chrome,editField,,,,,,,INPUT,text,Name_First,TEST,,,,\n" +
                "2019-04-29T16:51:42.795Z,st,Chrome,paste,,hey,,,,,INPUT,text,Name_First,hey,,,,\n" +
                "2019-04-29T16:51:44.332Z,st,Chrome,paste,,hey,,,,,INPUT,text,Name_First,heyhey,,,,\n" +
                "2019-04-29T16:51:45.657Z,st,Chrome,editField,,,,,,,INPUT,text,Name_First,heyheyhey,,,,\n";

        assertThat(WriteSimplifier.containsRedundantEditField(logs), is(equalTo(true)));


        assertEquals("2019-04-29T16:51:42.795Z,st,Chrome,paste,,hey,,,,,INPUT,text,Name_First,hey,,,,\n" +
                        "2019-04-29T16:51:44.332Z,st,Chrome,paste,,hey,,,,,INPUT,text,Name_First,heyhey,,,,\n" +
                        "2019-04-29T16:51:45.657Z,st,Chrome,editField,,,,,,,INPUT,text,Name_First,heyheyhey,,,,\n",
                WriteSimplifier.removeRedundantEditField(logs));
    }
}

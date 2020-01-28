package pre_processing;

import com.simplifier.pre_processing.PreProcessing;
import org.junit.Test;

import static org.junit.Assert.assertEquals;

public class PreProcessingTest {


    @Test
    public void testSortLog() {
        String logs = "2019-04-02T17:51:41.579Z,st,Excel,getCell,,,excel.xlsx,Sheet1,A1,,,,,[[3]],,,,\n" +
                "2019-04-02T17:59:44.697Z,st,Chrome,clickTextField,,,,,,,INPUT,text,SingleLine,,,,,\n" +
                "2019-04-02T17:55:41.579Z,st,Excel,getCell,,,excel.xlsx,Sheet1,A2,,,,,[[3]],,,,\n";

        assertEquals(PreProcessing.sortLog(logs),
                "2019-04-02T17:51:41.579Z,st,Excel,getCell,,,excel.xlsx,Sheet1,A1,,,,,[[3]],,,,\n" +
                        "2019-04-02T17:55:41.579Z,st,Excel,getCell,,,excel.xlsx,Sheet1,A2,,,,,[[3]],,,,\n" +
                        "2019-04-02T17:59:44.697Z,st,Chrome,clickTextField,,,,,,,INPUT,text,SingleLine,,,,,\n");
    }

    @Test
    public void testDeleteChromeClipboardCopy() {
        String logs = "2019-04-02T17:56:41.572Z,st,Excel,getCell,,,excel.xlsx,Sheet1,A1,,,,,[[1]],,,,\n" +
                "2019-04-03T06:28:15.648Z,st,Chrome,copy,,text,,,,,INPUT,text,Name_First,test,,,,\n" +
                "2019-04-02T17:56:41.899Z,,OS-Clipboard,copy,,text,,,,,,,,,,,,\n" +
                "2019-04-02T17:56:41.578Z,st,Excel,getCell,,,excel.xlsx,Sheet1,C1,,,,,[[3]],,,,";

        assertEquals(PreProcessing.deleteChromeClipboardCopy(logs),
                "2019-04-02T17:56:41.572Z,st,Excel,getCell,,,excel.xlsx,Sheet1,A1,,,,,[[1]],,,,\n" +
                        "2019-04-03T06:28:15.648Z,st,Chrome,copy,,text,,,,,INPUT,text,Name_First,test,,,,\n" +
                        "2019-04-02T17:56:41.578Z,st,Excel,getCell,,,excel.xlsx,Sheet1,C1,,,,,[[3]],,,,");
    }

    @Test
    public void testGetCellClipboardCopy() {
        String logs = "2019-04-02T17:56:40.572Z,st,Excel,getCell,,,excel.xlsx,Sheet1,A1,,,,,[[1]],,,,\n" +
                "2019-04-02T17:56:41.587Z,st,Chrome,clickTextField,,,,,,,INPUT,text,SingleLine,,,,,\n" +
                "2019-04-02T17:56:42.656Z,st,Chrome,editField,,,,,,,INPUT,text,SingleLine,3,,,,\n" +
                "2019-04-02T17:56:43.593Z,st,Excel,getCell,,,excel.xlsx,Sheet1,B1,,,,,[[2]],,,,\n" +
                "2019-04-02T17:56:44.899Z,,OS-Clipboard,copy,,3,,,,,,,,,,,,\n" +
                "2019-04-02T17:56:45.578Z,st,Excel,getCell,,,excel.xlsx,Sheet1,C1,,,,,[[3]],,,,";

        assertEquals(PreProcessing.mergeNavigationCellCopy(logs),
                "2019-04-02T17:56:41.587Z,st,Chrome,clickTextField,,,,,,,INPUT,text,SingleLine,,,,,\n" +
                        "2019-04-02T17:56:42.656Z,st,Chrome,editField,,,,,,,INPUT,text,SingleLine,3,,,,\n" +
                        "2019-04-02T17:56:44.899Z,st,Excel,copyCell,,3,excel.xlsx,Sheet1,B1,,,,,[[2]],,,,\n");
    }

    @Test
    public void testGetRangeClipboardCopy() {
        String logs = "2019-04-09T15:15:43.049Z,st,Excel,getCell,,,test.xlsx,Sheet1,G4,,,,,\"[[]]\",,,,\n" +
                "2019-04-09T15:15:45.862Z,st,Excel,getRange,,,test.xlsx,Sheet1,A1:F1,,,,,\"[[1,2,3,4,5,6]]\",,,,\n" +
                "2019-04-09T15:15:46.349Z,,OS-Clipboard,copy,,123456,,,,,,,,,,,,\n" +
                "2019-04-09T15:15:46.869Z,st,Excel,getCell,,,test.xlsx,Sheet1,F8,,,,,\"[[]]\",,,,\n";

        assertEquals(PreProcessing.mergeNavigationCellCopy(logs),
                "2019-04-09T15:15:46.349Z,st,Excel,copyRange,,123456,test.xlsx,Sheet1,A1:F1,,,,,\"[[1,2,3,4,5,6]]\",,,,\n");
    }

    @Test
    public void testEditCellClipboardCopy() {
        String logs = "2019-04-09T15:15:43.049Z,st,Excel,getCell,,,test.xlsx,Sheet1,G4,,,,,\"[[]]\",,,,\n" +
                "2019-04-09T15:15:45.862Z,st,Excel,getRange,,,test.xlsx,Sheet1,A1:F1,,,,,\"[[1,2,3,4,5,6]]\",,,,\n" +
                "2019-04-09T15:15:46.372Z,st,Excel,editCell,,,test.xlsx,Sheet1,F2,,,,,6,,,,\n" +
                "2019-04-09T15:15:47.349Z,,OS-Clipboard,copy,,6,,,,,,,,,,,,\n" +
                "2019-04-09T15:15:48.869Z,st,Excel,getCell,,,test.xlsx,Sheet1,F8,,,,,\"[[]]\",,,,\n";

        assertEquals(PreProcessing.mergeNavigationCellCopy(logs),
                "2019-04-09T15:15:46.372Z,st,Excel,editCell,,,test.xlsx,Sheet1,F2,,,,,6,,,,\n" +
                        "2019-04-09T15:15:47.349Z,st,Excel,copyCell,,6,test.xlsx,Sheet1,F2,,,,,6,,,,\n");
    }
}


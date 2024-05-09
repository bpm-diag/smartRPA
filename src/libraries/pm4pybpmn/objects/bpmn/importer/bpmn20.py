from libraries.pm4pybpmn.objects.bpmn.importer.bpmn_diagram_import import BpmnDiagramGraphImport
from libraries.pm4pybpmn.objects.bpmn.importer import bpmn_diagram_rep as diagram


def import_bpmn(file_path):
    """
    Import a BPMN 2.0 diagram from an XML file

    Parameters
    ----------
    file_path
        File where the XML file is saved

    Returns
    ----------
    bpmn_graph
        BPMN graph object
    """
    bpmn_graph = diagram.BpmnDiagramGraph()
    BpmnDiagramGraphImport.load_diagram_from_xml(file_path, bpmn_graph)
    return bpmn_graph

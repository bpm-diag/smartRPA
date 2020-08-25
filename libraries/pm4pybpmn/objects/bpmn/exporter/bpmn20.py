import os

from libraries.pm4pybpmn.objects.bpmn.exporter.bpmn_diagram_export import BpmnDiagramGraphExport
import tempfile


def export_bpmn(bpmn_graph, file_path):
    """
    Export a BPMN 2.0 diagram from a BPMN graph object

    Parameters
    ----------
    bpmn_graph
        BPMN graph
    file_path
        Path where the diagram should be exported
    """
    directory = str(os.path.dirname(file_path))
    if len(directory) == 0:
        directory = os.getcwd()
    file_path = os.path.basename(file_path)
    directory = directory.replace("\\", "\\\\")
    directory = directory + os.sep
    BpmnDiagramGraphExport.export_xml_file(directory, file_path, bpmn_graph)


def get_string_from_bpmn(bpmn_graph):
    """
    Get an XML string from a BPMN graph

    Parameters
    ------------
    bpmn_graph
        BPMN graph

    Returns
    -----------
    xml_string
        XML string representing the BPMN
    """
    file_complete_path = tempfile.NamedTemporaryFile(suffix='.bpmn').name
    directory = str(os.path.dirname(file_complete_path))
    file_path = os.path.basename(file_complete_path)
    directory = directory.replace("\\", "\\\\")
    directory = directory + os.sep
    BpmnDiagramGraphExport.export_xml_file(directory, file_path, bpmn_graph)
    return open(file_complete_path, "r").read()
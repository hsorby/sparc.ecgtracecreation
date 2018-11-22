from opencmiss.zinc.context import Context
from opencmiss.utils.zinc import create_finite_element_field
from opencmiss.zinc.element import Elementbasis, Element

CHANNEL_LOCATION_DATABASE = {
    '18': [1.0, 1.0],
    '34': [4.0, 1.0],
    '38': [6.8, 1.0],
    '27': [1.2, 3.5],
    '30': [3.2, 3.4],
    '35': [5.5, 4.1],
    '39': [8.6, 3.3],
    '28': [1.8, 5.6],
    '31': [3.8, 4.9],
    '32': [4.3, 6.0],
    '36': [6.6, 6.0],
    '40': [8.7, 5.4],
    '29': [2.3, 8.0],
    '33': [5.0, 7.5],
    '37': [8.2, 7.3],
}

ELEMENT_NODES_STATIC_SIZE = [
    [18, 34, 27],
    [27, 34, 30],
    [27, 30, 28],
    [28, 30, 31],
    [28, 31, 29],
    [29, 31, 32],
    [29, 32, 33],
    [34, 38, 30],
    [30, 38, 35],
    [30, 35, 31],
    [31, 35, 32],
    [38, 39, 35],
    [35, 36, 32],
    [32, 36, 33],
    [35, 39, 36],
    [36, 39, 40],
    [36, 40, 37],
    [33, 36, 37],
]

ELEMENT_NODES_VARIED_SIZE = [
    [18, 34, 27, 30],
    [34, 38, 30, 35],
    [38, 39, 35],
    [27, 30, 28, 31],
    [30, 35, 31, 32],
    [35, 39, 32, 36],
    [39, 40, 36],
    [28, 31, 29, 32],
    [32, 36, 29, 33],
    [36, 40, 33, 37],
]

ELEMENT_NODES = ELEMENT_NODES_VARIED_SIZE


def create_mesh(data):
    context = Context('ecg')
    region = context.createRegion()
    coordinate_field = create_finite_element_field(region, dimension=2)
    ecg_field = create_finite_element_field(region, field_name='ecg', dimension=1, type_coordinate=False)

    keys = list(data.keys())
    time_sequence = define_time_sequence(data[keys[0]])

    result = create_nodes(coordinate_field, ecg_field, data, time_sequence)
    if result is None:
        return result, time_sequence
    result = create_elements([coordinate_field, ecg_field])
    if result is None:
        return result, time_sequence

    return region, time_sequence


def create_nodes(finite_element_field, ecg_field, data, time_sequence):
    field_module = finite_element_field.getFieldmodule()

    node_set = field_module.findNodesetByName('nodes')
    node_template = node_set.createNodetemplate()

    node_template.defineField(finite_element_field)
    node_template.defineField(ecg_field)

    zinc_time_sequence = field_module.getMatchingTimesequence(time_sequence)
    node_template.setTimesequence(ecg_field, zinc_time_sequence)

    field_cache = field_module.createFieldcache()
    for key in data:
        if key in CHANNEL_LOCATION_DATABASE:
            node = node_set.createNode(int(key), node_template)
            field_cache.setNode(node)
            finite_element_field.assignReal(field_cache, CHANNEL_LOCATION_DATABASE[key])
            for index, value in enumerate(data[key]):
                time = time_sequence[index]
                field_cache.setTime(time)
                ecg_field.assignReal(field_cache, value)
        else:
            return None

    return 0


def create_elements(finite_element_fields):
    field_module = finite_element_fields[0].getFieldmodule()

    mesh = field_module.findMeshByDimension(2)
    bi_linear_lagrange_basis = field_module.createElementbasis(2, Elementbasis.FUNCTION_TYPE_LINEAR_LAGRANGE)
    eft_bi_linear_lagrange = mesh.createElementfieldtemplate(bi_linear_lagrange_basis)
    bi_linear_simplex_basis = field_module.createElementbasis(2, Elementbasis.FUNCTION_TYPE_LINEAR_SIMPLEX)
    eft_bi_linear_simplex = mesh.createElementfieldtemplate(bi_linear_simplex_basis)

    element_template_square = mesh.createElementtemplate()
    element_template_square.setElementShapeType(Element.SHAPE_TYPE_SQUARE)
    for f in finite_element_fields:
        element_template_square.defineField(f, -1, eft_bi_linear_lagrange)

    element_template_triangle = mesh.createElementtemplate()
    element_template_triangle.setElementShapeType(Element.SHAPE_TYPE_TRIANGLE)
    for f in finite_element_fields:
        element_template_triangle.defineField(f, -1, eft_bi_linear_simplex)

    for element_nodes in ELEMENT_NODES:

        if len(element_nodes) == 4:
            element_template = element_template_square
            eft = eft_bi_linear_lagrange
        else:
            element_template = element_template_triangle
            eft = eft_bi_linear_simplex

        element = mesh.createElement(-1, element_template)
        element.setNodesByIdentifier(eft, element_nodes)

    return 0


def define_time_sequence(values):
    """
    Assuming the values are measured at a rate of 1000 Hz.
    :param values:
    :return:
    """
    num = len(values)
    stop = num / 1000.0

    return [i * stop / (num - 1) for i in range(num)]

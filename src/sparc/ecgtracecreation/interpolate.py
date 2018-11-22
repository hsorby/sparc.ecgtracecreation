from opencmiss.zinc.field import FieldFindMeshLocation, Field


def evaluate_8x8_grid(region, time_sequence):
    electrode_data = {}
    field_module = region.getFieldmodule()
    mesh = field_module.findMeshByDimension(2)

    ecg_field = field_module.findFieldByName('ecg')
    field_cache = field_module.createFieldcache()

    x_stops = define_sequence(2.1, 7.5, 8)
    y_stops = define_sequence(1.5, 7.1, 8)

    element_group = field_module.createFieldElementGroup(mesh)
    mesh_group = element_group.getMeshGroup()
    element_iterator = mesh.createElementiterator()

    element = element_iterator.next()
    while element.isValid():
        mesh_group.addElement(element)
        element = element_iterator.next()

    electrode_id = 0

    for x in x_stops:
        for y in y_stops:
            electrode_id += 1
            element, xi = find_mesh_location([x, y], field_module, mesh_group)
            field_cache.setMeshLocation(element, xi)
            ecg_values = []
            for time in time_sequence:
                field_cache.setTime(time)
                _, ecg_value = ecg_field.evaluateReal(field_cache, 1)
                ecg_values.append(ecg_value)

            electrode_data['{0}'.format(electrode_id)] = ecg_values

    # write_model(region)

    return electrode_data


def find_mesh_location(desired_coordinates, field_module, mesh_group):
    coordinate_field = field_module.findFieldByName('coordinates')
    electrode_location_field = field_module.createFieldConstant(desired_coordinates)
    find_mesh_location_field = field_module.createFieldFindMeshLocation(electrode_location_field,
                                                                        coordinate_field, mesh_group)
    find_mesh_location_field.setSearchMode(FieldFindMeshLocation.SEARCH_MODE_NEAREST)

    field_cache = field_module.createFieldcache()

    found_element, xi_location = find_mesh_location_field.evaluateMeshLocation(field_cache, 2)
    # print(found_element.isValid(), found_element.getIdentifier(), xi_location)
    return found_element, xi_location


def define_sequence(start, stop, num):
    """
    Assuming the values are measured at a rate of 1000 Hz.
    :param values:
    :return:
    """
    return [start + i * (stop - start) / (num - 1) for i in range(num)]


def write_model(region):
    file_name = 'bob.ex2'
    streamInfo = region.createStreaminformationRegion()
    file = streamInfo.createStreamresourceFile(file_name)
    streamInfo.setResourceDomainTypes(file,
        Field.DOMAIN_TYPE_NODES | Field.DOMAIN_TYPE_MESH1D | Field.DOMAIN_TYPE_MESH2D | Field.DOMAIN_TYPE_MESH3D)
    region.write(streamInfo)

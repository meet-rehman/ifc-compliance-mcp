import ifcopenshell
import ifcopenshell.api
import ifcopenshell.util.element


def generate_gold_plot_ifc(output_path, plot_name, site_area_m2, footprint_area_m2, gold_grz):
    """Creates a minimal IFC file encoding one of your verified gold-answer plots
    as properties (not full 3D geometry) so it's simple, robust, and directly
    comparable to your benchmark's verified numbers."""
    model = ifcopenshell.api.run("project.create_file")
    project = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcProject", name=plot_name)
    ifcopenshell.api.run("unit.assign_unit", model)

    site = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcSite", name=f"{plot_name} - Site")
    building = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcBuilding", name=f"{plot_name} - Building")

    # NOTE: some ifcopenshell versions use `product=`, others `products=[...]` here —
    # if this errors, check ifcopenshell.api.aggregate.assign_object's signature in your installed version.
    ifcopenshell.api.run("aggregate.assign_object", model, relating_object=project, products=[site])
    ifcopenshell.api.run("aggregate.assign_object", model, relating_object=site, products=[building])

    pset_site = ifcopenshell.api.run("pset.add_pset", model, product=site, name="Pset_PlotData")
    ifcopenshell.api.run("pset.edit_pset", model, pset=pset_site, properties={"SiteArea_m2": site_area_m2})

    pset_building = ifcopenshell.api.run("pset.add_pset", model, product=building, name="Pset_PlotData")
    ifcopenshell.api.run("pset.edit_pset", model, pset=pset_building, properties={
        "FootprintArea_m2": footprint_area_m2,
        "VerifiedGoldGRZ": gold_grz,
    })

    model.write(output_path)
    return output_path


def calculate_coverage_ratio(ifc_path):
    """Opens an IFC file and computes the actual built coverage ratio from its
    stored plot data properties."""
    model = ifcopenshell.open(ifc_path)

    site_area = None
    footprint_area = None

    for site in model.by_type("IfcSite"):
        for pset in ifcopenshell.util.element.get_psets(site).values():
            if "SiteArea_m2" in pset:
                site_area = pset["SiteArea_m2"]

    for building in model.by_type("IfcBuilding"):
        for pset in ifcopenshell.util.element.get_psets(building).values():
            if "FootprintArea_m2" in pset:
                footprint_area = pset["FootprintArea_m2"]

    if site_area is None or footprint_area is None:
        raise ValueError("Could not find SiteArea_m2 or FootprintArea_m2 in the IFC file")

    return {
        "site_area_m2": site_area,
        "footprint_area_m2": footprint_area,
        "computed_coverage_ratio": round(footprint_area / site_area, 3),
    }

def read_plot_metadata(ifc_path):
    """Reads back the plot name and stored gold GRZ from an IFC file's own properties."""
    model = ifcopenshell.open(ifc_path)
    project = model.by_type("IfcProject")[0]
    plot_name = project.Name

    gold_grz = None
    for building in model.by_type("IfcBuilding"):
        for pset in ifcopenshell.util.element.get_psets(building).values():
            if "VerifiedGoldGRZ" in pset:
                gold_grz = pset["VerifiedGoldGRZ"]

    return {"plot_name": plot_name, "gold_grz": gold_grz}    
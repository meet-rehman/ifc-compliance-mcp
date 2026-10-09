# generate_test_ifc.py
from ifc_tools import generate_gold_plot_ifc

GOLD_PLOTS = [
    {"slug": "plot_18a", "plot_name": "Plot 18A - Buergerhospital/Tuerlenstrasse", "gold_grz": 0.8},
    {"slug": "weg_71", "plot_name": "Weg 71 - Liselotte-Buehler-Weg, Bad Cannstatt", "gold_grz": 0.6},
    {"slug": "plot_9337", "plot_name": "Plot 9337 - Planstrasse C, Nordbahnhofstrasse", "gold_grz": 0.6},
    {"slug": "plot_20", "plot_name": "Plot 20 - Archivstrasse/Urbanstrasse (Stgt 306.1)", "gold_grz": 0.9},
    {"slug": "plot_9432_3", "plot_name": "Plot 9432/3 - Am Weissenhof (Stgt 322.1)", "gold_grz": 0.7},
    {"slug": "gb_lenbachstrasse", "plot_name": "GB Zone - Lenbachstrasse, Killesberg", "gold_grz": 0.6},
    {"slug": "wr1_lenbachstrasse", "plot_name": "WR1 Zone - Lenbachstrasse, Killesberg", "gold_grz": 0.45},
    {"slug": "wr2_lenbachstrasse", "plot_name": "WR2 Zone - Lenbachstrasse, Killesberg", "gold_grz": 0.4},
    {"slug": "gb_eierstrasse", "plot_name": "GB Zone - Eierstrasse, Heslach", "gold_grz": 0.4},
    {"slug": "so_hemminger", "plot_name": "SO Zone - Hemminger Strasse, Weilimdorf", "gold_grz": 0.25},
]

SITE_AREA_M2 = 1000

# add here: real ALKIS/Hausumringe-derived plots, alongside GOLD_PLOTS above
REAL_GOLD_PLOTS = [
    {"slug": "plot_18a_real", "plot_name": "Plot 18A - Buergerhospital (real ALKIS geometry)",
     "gold_grz": 0.8, "site_area_m2": 10151.07, "footprint_area_m2": 3104.82},
    {"slug": "plot_20_real", "plot_name": "Plot 20 - Archivstrasse/Urbanstrasse (real ALKIS geometry)",
     "gold_grz": 0.9, "site_area_m2": 12580.63, "footprint_area_m2": 7391.64},
]

if __name__ == "__main__":
    for plot in GOLD_PLOTS:
        footprint = plot["gold_grz"] * SITE_AREA_M2
        path = generate_gold_plot_ifc(
            output_path=f"sample_data/{plot['slug']}.ifc",
            plot_name=plot["plot_name"],
            site_area_m2=SITE_AREA_M2,
            footprint_area_m2=footprint,
            gold_grz=plot["gold_grz"],
        )
        print(f"{plot['slug']}: GRZ={plot['gold_grz']} -> {path}")

    # add here: generate the two real-geometry plots as a second pass
    for plot in REAL_GOLD_PLOTS:
        path = generate_gold_plot_ifc(
            output_path=f"sample_data/{plot['slug']}.ifc",
            plot_name=plot["plot_name"],
            site_area_m2=plot["site_area_m2"],
            footprint_area_m2=plot["footprint_area_m2"],
            gold_grz=plot["gold_grz"],
        )
        print(f"{plot['slug']}: GRZ={plot['gold_grz']} (real geometry) -> {path}")
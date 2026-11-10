VERSION = "v0.2.0"


class Texts:
    title = f"HydroFIA ({VERSION})"

    show_help = "Visa hjälp"

    get_hydrofia_export_button = "Välj .txt-fil från HydroFIA"
    get_template_path_button = "Välj rättningsfil"
    get_ctd_directory_button = "Välj mapp för ctd-filer (standardformat)"
    get_template_directory_button = "Välj exportmapp"

    non_existing_hydrofia_path = "Den valda hydrofia-filen existerar inte..."
    non_existing_template_path = "Den valda mallen existerar inte..."
    non_existing_ctd_path = "Den valda mappen för ctd-filer existerar inte..."

    missing_hydrofia_file_path = "Ingen exportfil från hydrofia vald..."
    missing_template_directory = "Ingen mapp för mall vald..."
    missing_ctd_directory = "Ingen mapp för ctd vald..."
    missing_template_path = "Ingen data tillgänglig..."
    missing_use_template_path = "Ingen rättningsfil vald..."
    missing_result_path = "Ingen resultatfil bestämd..."

    dialog_title_ctd_directory = "Välj ctd-mapp"
    dialog_title_template_directory = "Välj mapp där du vill lägga din mall"
    dialog_title_template_file = "Välj den mallen som du vill använda"
    dialog_title_hydrofia_file_path = (
        "Välj den exportfil från Hydrofia som du vill använda"
    )

    open_directory = "Öppna mapp"
    open_file_template = "Öppna rättningsfil"
    open_file_result = "Öppna resultatfil"

    create_template = "Skapa rättningsfil"
    create_result = "Skapa resultatfil"

    # overwrite = 'Vill du skriva över filen?'

    info_creating_template = "Mall skapas! Vänta..."
    info_creating_result = "Resultatfil skapas! Vänta..."

    template_export_file_name = "Ange namn på din Hydro FIA excelfil som ska skapas"
    result_file_name = "Välj ev. namn på resultatfil"
    create_file_label = "Fil som kommer att skapas:"

    signature = "Din signatur"
    project = "Projekt"

    surface_layer = "Avstånd vid ytan [m]"
    bottom_layer = "Avstånd vid botten [m]"
    max_depth_diff_allowed = "Max avstånd [m]"
    reset_depth_margins = "Återställ"
    title_ctd_matching = "CTD-matchning"
    title_metadata = "Metadata"

    title_merge_ctd_with_hydrofia = "Skapa resultatfil"
    title_create_excel = "Skapa rättningsfil"
    period_filter_label = "Filtrera på period:"

    tab_crm = "CRM"
    tab_tris = "TRIS"
    tris_title = "Beräkna pH med TRIS"

    title_title = "Beräkna pH med CRM"
    batch_salinity = "Salinitet"
    batch_temperature = "Temperatur"
    temperature = "Temperatur"
    measured_ph = "Uppmätt pH"
    batch_alk_label = "ALK i batch"
    batch_dic_label = "DIC i batch"
    batch_salt_label = "Salthalt i batch"
    deviation = "Avvikelse"
    calculated_ph = "Beräknat pH"

    # Texts with parameters
    def invalid_hydrofia_file(self, file_name: str) -> str:
        return (
            f"{file_name} ser inte ut som en exportfil från HydroFIA. "
            "Välj txt-filen som HydroFIA har exporterat."
        )

    def invalid_batch(self, batch_nr: str) -> str:
        return f"Batch {batch_nr} saknar värden som behövs. Välj en annan batch."

    def select_overwrite(self, path):
        return (
            f"Filen finns redan. "
            f"Du måste välja att skriva över filen om du vill fortsätta: {path}"
        )

    def get_file_exists(self, status):
        if status:
            return "Filen finns redan. Vill du skriva över den?"
        return "Filen finns inte."

    def info_creating_template_done(self, path):
        return f"Rättningsfil har skapats: {path}"

    def get_info_creating_result_done(self, path):
        return f"Resultatfil har skapats: {path}"

    def missing_metadata(self, meta: str) -> str:
        return f"Metadata saknas: {meta}"


class UnderwayTexts:
    title = f"HydroFIA Underway ({VERSION})"
    card_title = "Beräkna pH för underway-data"

    get_input_files_button = "Välj indatafiler"
    get_output_directory_button = "Välj exportmapp"
    convert = "Konvertera"
    create_files_label = "Filer som kommer att skapas:"

    missing_input_files = "Inga indatafiler valda..."
    missing_output_directory = "Ingen exportmapp vald..."
    missing_result_path = "Välj indatafiler och exportmapp..."
    non_existing_output_directory = "Den valda exportmappen existerar inte..."
    duplicate_result_paths = (
        "Flera indatafiler har samma namn och skulle ge samma resultatfil. "
        "Välj filer med olika namn."
    )
    select_overwrite_files = (
        "Några av filerna finns redan. "
        "Du måste välja att skriva över dem om du vill fortsätta."
    )

    dialog_title_input_files = "Välj filerna med underway-data"
    dialog_title_output_directory = "Välj mapp där resultatet ska sparas"

    def invalid_underway_file(self, file_name: str) -> str:
        return (
            f"{file_name} ser inte ut som en Underway-fil. Välj en annan fil."
        )

    def non_existing_input_file(self, path) -> str:
        return f"Indatafilen existerar inte: {path}"

    def files_exist(self, nr: int) -> str:
        if nr == 1:
            return "1 av filerna finns redan. Vill du skriva över den?"
        return f"{nr} av filerna finns redan. Vill du skriva över dem?"

    def converting(self, nr: int, total: int, name: str) -> str:
        return f"Konverterar fil {nr} av {total}: {name}. Vänta..."

    def convert_failed(self, name: str, nr_done: int, error: Exception) -> str:
        return (
            f"Något gick fel med {name}:\n{error}\n"
            f"{nr_done} fil(er) hann konverteras. Resten har inte konverterats."
        )

    def converted(self, nr: int, directory) -> str:
        return f"{nr} fil(er) har skapats i {directory}"

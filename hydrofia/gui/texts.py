
class Texts:

    @property
    def title(self):
        return 'HydroFIA'

    @property
    def get_hydrofia_export_button(self):
        return 'Välj .txt-fil från HydroFIA'

    @property
    def get_template_path_button(self):
        return 'Välj rättningsfil'

    @property
    def get_ctd_directory_button(self):
        return 'Välj mapp för ctd-filer (standardformat)'

    @property
    def get_template_directory_button(self):
        return 'Välj exportmapp'

    @property
    def non_existing_hydrofia_path(self):
        return 'Den valda hydrofia-filen existerar inte...'

    @property
    def non_existing_template_path(self):
        return 'Den valda mallen existerar inte...'

    @property
    def non_existing_ctd_path(self):
        return 'Den valda mappen för ctd-filer existerar inte...'

    @property
    def missing_hydrofia_file_path(self):
        return 'Ingen exportfil från hydrofia vald...'

    @property
    def missing_template_directory(self):
        return 'Ingen mapp för mall vald...'

    @property
    def missing_ctd_directory(self):
        return 'Ingen mapp för ctd vald...'

    @property
    def missing_template_path(self):
        return 'Ingen data tillgänglig...'

    @property
    def missing_result_path(self):
        return 'Ingen resultatfil bestämd...'

    @property
    def dialog_title_ctd_directory(self):
        return 'Välj ctd-mapp'

    @property
    def dialog_title_template_directory(self):
        return 'Välj mapp där du vill lägga din mall'

    @property
    def dialog_title_template_file(self):
        return 'Välj den mallen som du vill använda'

    @property
    def dialog_title_hydrofia_file_path(self):
        return 'Välj den exportfil från Hydrofia som du vill använda'

    @property
    def open_directory(self):
        return 'Öppna mapp'

    @property
    def open_file(self):
        return 'Öppna fil'

    @property
    def create_template(self):
        return 'Skapa rättningsfil'

    @property
    def create_result(self):
        return 'Skapa resultatfil'

    # @property
    # def overwrite(self):
    #     return 'Vill du skriva över filen?'

    def select_overwrite(self, path):
        return f'Filen finns redan. Du måste välja att skriva över filen om du vill fortsätta: {path}'

    def get_file_exists(self, status):
        if status:
            return f'Filen finns redan. Vill du skriva över den?'
        return f'Filen finns inte.'

    @property
    def info_creating_template(self):
        return 'Mall skapas! Vänta...'

    @property
    def info_creating_result(self):
        return 'Resultatfil skapas! Vänta...'

    def info_creating_template_done(self, path):
        return f'Mall har skapats: {path}'

    def get_info_creating_result_done(self, path):
        return f'Resultatfil har skapats: {path}'

    @property
    def template_export_file_name(self):
        return 'Ange namn på din Hydro FIA excelfil som ska skapas'

    @property
    def result_file_name(self):
        return 'Välj ev. namn på resultatfil'

    @property
    def create_file_label(self):
        return "Fil som kommer att skapas:"

    @property
    def signature(self):
        return 'Din signatur'

    @property
    def project(self):
        return 'Projekt'

    @property
    def surface_layer(self):
        return 'Tillåtet avstånd vid ytan [m] (för att matcha salt och temp)'

    @property
    def bottom_layer(self):
        return 'Tillåtet avstånd vid botten [m] (för att matcha salt och temp)'

    @property
    def max_depth_diff_allowed(self):
        return 'Max tillåtet avstånd för matching [m]'

    @property
    def reset_depth_margins(self):
        return 'Återställ'

    @property
    def title_merge_ctd_with_hydrofia(self):
        return 'Steg 3: Sammanfoga HydroFIA- och CTD data för att beräkna rätt salthalt och temperatur'

    @property
    def title_create_excel(self):
        return 'Steg 2: Skapa rättningsfil'

    @property
    def title_batch(self):
        return 'Steg 1: Beräkna pH från batch'

    def missing_metadata(self, meta: str) -> str:
        return f'Metadata saknas: {meta}'

    @property
    def batch_salinity(self) -> str:
        return 'Salinitet'

    @property
    def batch_temperature(self) -> str:
        return 'Temperatur'

    @property
    def batch_temp_label(self) -> str:
        return 'Temperatur:'

    @property
    def batch_measured_ph(self) -> str:
        return 'Uppmätt pH'

    @property
    def batch_alk_label(self) -> str:
        return 'ALK i batch:'

    @property
    def batch_dic_label(self) -> str:
        return 'DIC i batch:'

    @property
    def batch_salt_label(self) -> str:
        return 'Salthalt i batch:'

    @property
    def batch_plot_value_label(self) -> str:
        return 'Värde som ska plottas på kontrollkort:'

    @property
    def batch_ph_label(self) -> str:
        return 'Beräknat pH i batch:'

    @property
    def calculate_ph(self) -> str:
        return 'Beräkna pH'


library(tidyverse)
library(glue)
library(terra)
library(sf)
library(scico)
library(hrbrthemes)
library(classInt)
library(rdwd)
library(purrr)
library(leaflet)
library(lubridate)
library(gganimate)
# prepare temperature data

# download weather station list to decide from which station data to pull from
mydatapath <- "./data/"

# opendata_dwd_path <- "https://opendata.dwd.de/climate_environment/CDC/observations_germany/climate/daily/kl/recent/"
# 
# download.file(paste0(opendata_dwd_path, "KL_Tageswerte_Beschreibung_Stationen.txt"),
#               paste0(mydatapath, "weatherstations.txt"))

header <- read_table(file = paste0(mydatapath, "weatherstations.txt"),
                      col_names = FALSE,
                      n_max = 1)
weatherdata <- read_table(file = paste0(mydatapath, "weatherstations.txt"),
                          col_names = FALSE,
                          locale = locale(encoding = "WINDOWS-1252"),
                          skip = 2)
colnames(weatherdata) <- header[1, ]


# Select only those stations that provide data between 1961 and 2021
sixty_year_weather_data <- weatherdata |> 
  select(c(1:7)) |>  
  filter(von_datum <= as.numeric(19610101)) |>  
  filter(bis_datum >= as.numeric(20211231)) |> 
  mutate(Stations_id = as.integer(Stations_id))

# Pull data from one weather station
save_one_weatherstation <- function(weatherstation_id) {
  # get DWD download link by weatherstaion id
  link <- selectDWD(id=toString(weatherstation_id), res="daily", var="kl", per="hist") 
  
  # Actually download that dataset, returning the local storage file name:
  file <- dataDWD(link, read=FALSE)
  
  # Read each weatherstation file from the zip folder and save as .rds into ./data/ folder
  readDWD(file, varnames=TRUE) |> 
    select(c(STATIONS_ID, MESS_DATUM, TNK.Lufttemperatur_Min)) |>
    saveRDS(file = glue('./data/min', weatherstation_id, '.rds'))
}

# Use previously filtered weather station ids to pull data from each of them and save to data folder 
# map(sixty_year_weather_data$Stations_id, save_one_weatherstation)

# Read in .rds files from ./data/ folder
combined_rds_files <- list.files( path = "./data/min", pattern = "*.rds", full.names = TRUE ) %>%
  map_dfr(readRDS)

# filter only those temperature per day values between 1961 and 2021
filtered_data_by_timeframe <- combined_rds_files %>%
  filter(MESS_DATUM >= "1961-01-01", MESS_DATUM <= "2021-01-01")

# prepare spatial data to visualize temperature

# read in counties
# source of shapefile: https://gdz.bkg.bund.de/index.php/default/digitale-geodaten/verwaltungsgebiete/nuts-gebiete-1-250-000-stand-31-12-nuts250-31-12.html
counties <- st_read("nuts250_1231/250_NUTS1.shp") 

# filter only those days where the temperature is -10 degrees or less
station_id_values_per_year <- filtered_data_by_timeframe |>
  filter(TNK.Lufttemperatur_Min < (-10)) |> 
  group_by(STATIONS_ID, year = lubridate::floor_date(MESS_DATUM, "year")) |>
  count() |>
  rename(Stations_id = STATIONS_ID) |>
  rename(n_days = n) |>
  mutate(n_days = replace_na(n_days, 0))
  
# join 'station_id_values_per_year' to also include latitude and longitude for viz
joined_spatial_df <- left_join(station_id_values_per_year, sixty_year_weather_data, by = "Stations_id") |> 
  mutate(y = year(year)) |> 
  st_as_sf(coords = c("geoLaenge", "geoBreite")) |> 
  st_set_crs("epsg:4326") |> 
  st_transform("epsg:31467") |> 
  mutate(year = year(year)) |> 
  arrange(Stations_id, year) 

# visualize data

p <- ggplot(data = counties) +
  geom_sf(fill = "white", size=0.15) +
  geom_sf(data=joined_spatial_df, aes(size = n_days, stroke = 0, alpha = I(ifelse(n_days < 1, 0, 0.7))), color="#0F52BA") +
  scale_size_binned(
    trans = "identity",
    breaks = c(0, 10, 20, 30, 40, 50),
    range = c(1, 2),
  )  +
  # transition_time(year) +
  facet_wrap(year ~ .,
             ncol = 10) +
  labs(title = "Sehr kalte Tage nehmen langsam ab",
       subtitle = "Anzahl an kalten Tagen pro Jahr unter -10°C",
       caption = "Daten: BKK & DWD") + 
  guides(fill = guide_legend(keyheight = unit(1, units = "mm"),  
                             keywidth = unit(3, units = "mm"),
                             direction = "horizontal",
                             nrow = 1,
                             ticks.colour = "white",
                             label.position = "bottom",
                             title.position = "bottom",
                             title.hjust = 0.5)) +
  theme_void() +
  theme(legend.direction="horizontal",
        legend.position="bottom", 
        legend.justification = "left",
        legend.box = "vertical",
        legend.title = element_blank(),
        text=element_text(family="Times New Roman"),
        panel.spacing.y = unit(1, "lines"),
        plot.background = element_rect(fill = 'white', colour = 'white'),
        plot.subtitle = element_text(size=15, 
                                   vjust=1, 
                                   color="black",
                                   margin = margin(.3,0,.5,0, "cm")),
        plot.title = element_text(size = 26, 
                                  face = "bold", 
                                  colour = 'black',
                                  margin = margin(.3,0,.5,0, "cm")),
        strip.background = element_rect(fill= alpha('#ffffff', 0.05), colour = NA),
        strip.text = element_text(size = 9, 
                                  face = "bold", 
                                  colour = '#000000',
                                  margin = margin(.1,0,.1,0, "cm")),
        plot.caption = element_text(size = 9,
                                    colour = '#000000',
                                    margin = margin(.5,0,.3,0, "cm")))

ggsave("anzahl_tage_pro_jahr_unter_minus_10_grad.jpg", dpi = 150, width = 1200, height = 1200, units = "px")


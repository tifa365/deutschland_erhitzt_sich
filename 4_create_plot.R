library(tidyverse)
library(sf)
library(rnaturalearth)
library(glue)

# Constants
TEMPERATURE_THRESHOLD <- 35
SHAPEFILE_PATH <- "nuts250_1231/250_NUTS1.shp"

# Read the GeoJSON file
data_path <- "dwd_weather_data/processed_station_data_per_year.geojson"
station_data <- st_read(data_path)

station_data <- station_data %>% filter(year >= 1963 & year <= 2022)

# Read shapefile for German counties
counties <- st_read(SHAPEFILE_PATH)

# Create the visualization
# Create the plot
p <- ggplot(data = counties) +
  geom_sf(fill = "white", size = 0.15) +
  geom_sf(data = station_data, 
          aes(size = n_days, stroke = 0, alpha = I(ifelse(n_days < 1, 0, 0.7))), 
          color = "#E64415") +
  scale_size_binned(
    trans = "identity",
    breaks = c(0, 1, 4, 8, 12, 16),
    range = c(1, 2.8)
  ) +
  facet_wrap(year ~ ., ncol = 10) +
  labs(title = "Deutschland erhitzt sich",
       subtitle = glue("Anzahl an Tagen pro Jahr über {TEMPERATURE_THRESHOLD}° Celsius"),
       caption = "Daten: Source Code: Tim Fangmeyer | BKK & DWD | Idee: Patrick Stotz") +
  guides(fill = guide_legend(keyheight = unit(1, units = "mm"),  
                             keywidth = unit(3, units = "mm"),
                             direction = "horizontal",
                             nrow = 1,
                             ticks.colour = "white",
                             label.position = "bottom",
                             title.position = "bottom",
                             title.hjust = 0.5)) +
  theme_void() +
  theme(legend.direction = "horizontal",
        legend.position = "bottom", 
        legend.justification = "left",
        legend.box = "vertical",
        legend.title = element_blank(),
        text = element_text(family = "Times New Roman"),
        panel.spacing.y = unit(1, "lines"),
        plot.background = element_rect(fill = 'white', colour = 'white'),
        plot.subtitle = element_text(size = 15, 
                                     vjust = 1, 
                                     color = "black",
                                     margin = margin(.3, 0, .5, 0, "cm")),
        plot.title = element_text(size = 26, 
                                  face = "bold", 
                                  colour = 'black',
                                  margin = margin(.3, 0, .5, 0, "cm")),
        strip.background = element_rect(fill = alpha('#ffffff', 0.05), colour = NA),
        strip.text = element_text(size = 9, 
                                  face = "bold", 
                                  colour = '#000000',
                                  margin = margin(.1, 0, .1, 0, "cm")),
        plot.caption = element_text(size = 9,
                                    colour = '#000000',
                                    margin = margin(.5, 0, .3, 0, "cm")))


# Save the plot

ggsave("hitzetage_deutschland.png", plot = p, dpi = 150, width = 1200, height = 1200, units = "px", bg = "white")

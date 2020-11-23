
library(data.table)
library(readxl)
library(yaml)
library(RPostgreSQL)

# Script pour construire la base EPA à l'émission à partir des fichiers excel 
# Il y a aussi une extraction des métriques et des exports en csv et en bdd

# Script d'extraction des données EPA à l'émission
# Info à récupérer:
# -type de source
# -nom du site (code)
# -source category (k)
# -source subcategory (L)
# -Facility (B)
# -City (C)
# -State (D)
# -Release Media (G)
# -Congénère (colonne AG)
# -Run ID (AC)
# -Test date (AD)
# -Detect - Non-Detect Flag (AH)
# -Emission Amount  (=Concentration As Reported) (AI)

folder_path <- "C:\\Users\\tmagnandebornier\\Desktop\\Sia\\Missions\\INERIS\\Besoin_2\\DIOXDB\\I-TEFs\\DB_EXCEL\\"
folder_output <- "C:\\Users\\tmagnandebornier\\Desktop\\Sia\\Missions\\INERIS\\Besoin_2\\"
file_transco <- "transco_variables_v6.xlsx"

export_en_bdd <- 1
export_en_csv <- 1

table_epa_emission <- 'epa_emission'

date_today <- format(Sys.Date(), format="%Y%m%d")

# Load yaml config file for BDD
if (Sys.info()[1] == "Windows") {
  # chercher info un cran au dessus du git
  dbInfo <- read_yaml("C:\\Users\\tmagnandebornier\\Desktop\\Sia\\Missions\\INERIS\\git\\ineris\\conf\\project_config.yml")
  
  DB_HOST <- dbInfo$`project-database`$hostname
  DB_NAME <- dbInfo$`project-database`$name
  DB_USER <- dbInfo$`project-database`$user
  DB_PASSWORD <- dbInfo$`project-database`$password
} else {
  message('Récupération des configs...')
  ENV <- yaml.load(rawToChar(base64decode(Sys.getenv(c("PROJECT_CONFIG")))))
  DB_HOST <- ENV$`project-database`$hostname
  DB_NAME <- ENV$`project-database`$name
  DB_USER <- ENV$`project-database`$user
  DB_PASSWORD <- ENV$`project-database`$password
}

# CONSTRUCTION D'UNE TABLE REGROUPANT TOUS LES FICHIERS A CONCATENER
## Récupérer les sous dossiers présents 
list_files <- list.files(folder_path, recursive = TRUE)

# Retirer ACTLEVEL.XLS, ALL_EFS.XLS, les fichiers avec SUM, _Sum ou _sum
# Tous les fichiers du dossier MISC_CAT
# Les fichiers .LOG
list_files <- list_files[!list_files %in% c("ACTLEVEL.XLS", "ALL_EFS.XLS")]
list_files <- list_files[!( grepl("SUM", list_files, fixed = TRUE) 
                            | grepl("_Sum", list_files, fixed = TRUE) 
                            | grepl("_sum", list_files, fixed = TRUE) 
                            | grepl("-sum", list_files, fixed = TRUE) 
                            | grepl("MISC_CAT", list_files, fixed = TRUE) 
                            | grepl(".LOG", list_files, fixed = TRUE) 
)]


# Définir la table regroupant les différentes colonnes
dt_total <- data.table()

## Pour chaque fichier (boucle sur les fichiers)
for(file_tmp in list_files){
  
  print(paste0("Traitement du fichier ", file_tmp))
  
  tryCatch(
    {
      good_sheet <- 0
      sheet = 0
      # Charger le fichier xls et les données du bon onglet
      while( sheet < 10 & good_sheet==0){
        sheet <- sheet + 1
        excel_tmp <- as.data.table(read_excel(paste0(folder_path, "\\", file_tmp), sheet=sheet))
        if( tolower(names(excel_tmp)[[1]]) == "epa id number" ){
          good_sheet <- 1
        } else if(tolower(names(excel_tmp)[[1]]) == "epa id"){
          good_sheet <- 1
          names(excel_tmp)[[1]] <- "epa id number"
        }
        
      }
      
      #colonne en plus pour certains: "Air Pollution Control Device   Temp (F)" 
      
      # Extraire les colonnes d'intérêts
      col_id <- which(gsub("\\s+"," ", tolower(names(excel_tmp))) %in% c("epa id number", "facility", "city", "state",
                                                                         "release media", "realease media",
                                                                         "source category", "source subcategory", "soruce subcategory",
                                                                         "run id", "test date", "substance", 
                                                                         "detect - non-detect flag", "detect- non-detect flag", "detect/non-detect flag", 
                                                                         "emission amount (=concentration as reported)", "emissions (=concentration as reported)", "emissions (concentration as reported)",
                                                                         "emission amount (=concentration as calculated)", "emissions (=concentration as calculated)",
                                                                         "emission amount (=concentration as calculated/ reported)", "emission amount (=concentration as reported)...36",
                                                                         "concentration units as reported", "concentration units as calculated",
                                                                         "concentration units as calculated/ reported"))
      
      dt_tmp <- excel_tmp[, ..col_id]
      print(paste0("Nombre de colonnes récupérées: ", length(col_id)))
      
      names(dt_tmp) <- c("epa id number", "facility", "city", "state","release media", 
                         "source category", "source subcategory", 
                         "run id", "test date", "substance", "detect - non-detect flag", 
                         "emission amount  (=concentration as reported)",
                         "concentration units as reported")
      
      # Mettre les dates en character
      dt_tmp[, "test date":=as.character(dt_tmp$`test date`)]
      
      # Forcer le run id à être en character (une date pour certains)
      dt_tmp[, "run id":=as.character(dt_tmp$`run id`)]
      
      # Ajouter le nom du fichier
      dt_tmp[, file:=file_tmp]
      
      # Ajouter les lignes à la table de résultat
      dt_total <- rbind(dt_total, dt_tmp)
      
    },    
    error = function(cond) {
      message(paste("Error in treating data"))
      message("Here is the original error message:")
      message(cond)
    }
  )
  
  
}

dt_etape1 <- copy(dt_total)
# dt_total <- copy(dt_etape1)

# #############################################
# # Extraire fichiers qui ne sont pas utilisés
# #############################################
dt_file <- unique(dt_total[,.(file)])
dt_file[,file_used:='yes']
dt_files_origine <- as.data.table(list.files(folder_path, recursive = TRUE))
setnames(dt_files_origine, 'V1', 'file')

dt_files_origine <- merge(dt_files_origine, dt_file, on='file', all.x=TRUE, all.y=TRUE)
dt_files_origine[, file_used:=ifelse(is.na(file_used), 'no', 'yes')]
list_files_deleted <- dt_files_origine[file_used=='no']$file

dt_files_origine[,.N,file_used]

# write.csv2(dt_files_origine, file=paste0(folder_output, "fichiers_utilises_", date_today, ".csv"))

# 233 fichiers utilisés ; 51 écartés

# #############################################
# # Créer des flags pour filtre
# #############################################

# Flager les lignes full NA
dt_total[, flag_is_na := rowSums(is.na(dt_total))==13]

# Flager les lignes correspondant aux run id "1-O-M23-1" et "2-O-M23-1" 
# car on retrouve systématiquement plusieurs valeurs différentes par échantillon
dt_total <- dt_total[, flag_run_id := `run id` %in% c("1-O-M23-1", "2-O-M23-1")]

# Mettre les concentrations en numérique
## changer les ".." en "." (1 ligne à défaut ds MWI-LAST/MWIMAJOR.XLS pour la substance 5F Other)
dt_total[, `emission amount  (=concentration as reported)`:=gsub("\\.\\.", ".", `emission amount  (=concentration as reported)`)]
## 
dt_total[,`emission amount  (=concentration as reported)`:=as.double(`emission amount  (=concentration as reported)`)]
dt_total <- dt_total[, flag_na_conc := is.na(`emission amount  (=concentration as reported)`)]

# #############################################
# # EXTRACTION DES CATEGORIES et sous catégories présentes
# #############################################
dt_category <- dt_total[,.N,.(`source category`, `source subcategory`)]
dt_category <- dt_category[order(`source category`, `source subcategory`)]
dt_category
# write.csv2(dt_category, file=paste0(folder_output, "category_subcategory_initial_", date_today, ".csv"))

# #############################################
# # Utilisation des matrices de transco pour créer des flags de suppression
# #############################################

# Charger les matrices de transco pour corriger 
dt_substance <- as.data.table(read_excel(paste0(folder_output, "\\", file_transco), sheet='transco_substance'))
dt_conso <- as.data.table(read_excel(paste0(folder_output, "\\", file_transco), sheet='transco_concentration'))
dt_detect <- as.data.table(read_excel(paste0(folder_output, "\\", file_transco), sheet='transco_detect'))
dt_categ <- as.data.table(read_excel(paste0(folder_output, "\\", file_transco), sheet='transco_category'))

# jointure avec les tables de transco pour modifier les modalités
dt_total <- merge(dt_total, dt_substance[, .(substance, proposition, keep)], 
                  by='substance', all.x=TRUE, all.y=FALSE)
dt_total <- dt_total[, flag_substance:=ifelse(keep=='yes' & !is.na(keep), FALSE, TRUE)]
dt_total[,":="(substance=proposition, keep=NULL)]
dt_total[,proposition:=NULL]

dt_total <- merge(dt_total, dt_conso[, .(`concentration units as reported`, proposition, concentration_unit, gaz_rate)], 
                  by="concentration units as reported", all.x=TRUE, all.y=FALSE)
dt_total[,":="(`concentration units as reported`=proposition)]
dt_total[,proposition:=NULL]

dt_total <- merge(dt_total, dt_detect[, .(`detect - non-detect flag`, proposition, keep)], 
                  by='detect - non-detect flag', all.x=TRUE, all.y=FALSE)
dt_total <- dt_total[,flag_detect:=ifelse(keep=='yes', FALSE, TRUE)]
dt_total[,":="(`detect - non-detect flag`=proposition, keep=NULL)]
dt_total[,proposition:=NULL]

dt_total <- merge(dt_total, dt_categ[, .(`source category`, `source subcategory`, proposition_category, proposition_subcategory)], 
                  by=c("source category", "source subcategory"), all.x=TRUE, all.y=FALSE)
dt_total[,":="(`source category` = proposition_category, `source subcategory` = proposition_subcategory)]
dt_total[,":="(proposition_category=NULL, proposition_subcategory=NULL)]

# reordonner les colonnes
dt_total <- dt_total[,.(`epa id number`, facility, city, state, `release media`, `run id`, `test date`, 
                        file, `source category`, `source subcategory`, substance, `detect - non-detect flag`,
                        `emission amount  (=concentration as reported)`, `concentration units as reported`,
                        concentration_unit, gaz_rate, flag_is_na, flag_na_conc, flag_run_id, flag_substance, flag_detect)]

# write.csv2(dt_total, file=paste0(folder_output, "base_epa_emission_avt_filtres_", date_today, ".csv"))

# #############################################
# # Etude des lignes supprimées par fichier et par cause
# #############################################

## Focus sur flag_is_na avant suppression
dt_full_na <- dt_total[flag_is_na==TRUE,]
dt_full_na[, (nb_lignes_na=.N), file]

# Raison de suppression par fichier et par catégorie
# On s'absout des lignes full_na
dt_no_na <- dt_total[flag_is_na==FALSE,]
dt_no_na[, total_lines:=.N, file]
# lignes avec des concentrations NA + perc
dt_no_na[,":="(total_conc_na=sum(as.numeric(flag_na_conc)), 
               total_subtance_out=sum(as.numeric(flag_substance)),
               total_detect=sum(as.numeric(flag_detect)),
               total_deletion=sum(as.numeric(flag_na_conc | flag_substance | flag_detect))), 
         file]

dt_no_na[,":="(perc_concontration_na=round(total_conc_na/total_lines, 2),
               perc_substance_out=round(total_subtance_out/total_lines, 2),
               perc_detect=round(total_detect/total_lines, 2),
               perc_deletion=round(total_deletion/total_lines, 2))]

dt_bilan_fichiers <- unique(dt_no_na[,.(file, total_lines, total_deletion, perc_deletion,
                                        total_conc_na, perc_concontration_na, 
                                        total_subtance_out, perc_substance_out,
                                        total_detect, perc_detect)])[order(file)]

dt_bilan_fichiers

# Voir principales causes
dt_bilan_fichiers[,.(perc_deletion_total=sum(total_deletion)/sum(total_lines),
                     perc_conc_na_total=sum(total_conc_na)/sum(total_lines),
                     perc_substance_out_total=sum(total_subtance_out)/sum(total_lines),
                     perc_detect_total=sum(total_detect)/sum(total_lines))]

# write.csv2(dt_bilan_fichiers, file=paste0(folder_output, "bilan_traitement_des_fichiers_", date_today, ".csv"))

# #############################################
# # Etude des lignes supprimées par fichier et par cause
# #############################################

# Etude des 69 916 lignes pour lesquelles on a pas de catégorie ou sous catégories
dt_no_cat <- dt_total[is.na(`source category`) & is.na(`source subcategory`)]

dt_no_cat[, .N, file]

dt_no_cat[flag_is_na==FALSE & flag_na_conc==FALSE]

# aucune ligne avec une concentration renseignée ne présente pas de catégorie
# ie si on a une concentration, on connait le code catégorie



# #############################################
# # Export de la base après filtres
# #############################################

dt_emission <- copy(dt_total)

# Filtrer les lignes non désirées
dt_emission <- dt_emission[flag_is_na==FALSE & flag_na_conc==FALSE 
                           & flag_run_id==FALSE & flag_substance==FALSE & flag_detect==FALSE,]

# reordonner les colonnes
dt_emission <- dt_emission[,.(`epa id number`, facility, city, state, `release media`, `run id`, `test date`, 
                              file, `source category`, `source subcategory`, substance, `detect - non-detect flag`,
                              `emission amount  (=concentration as reported)`, `concentration units as reported`,
                              concentration_unit, gaz_rate)]

# Export de la base en csv
if(export_en_csv){
  print("Preparing exportation into CSV...")
  write.csv2(dt_emission, file=paste0(folder_output, "base_emission_dioxdb_", date_today, ".csv"))
}



if(export_en_bdd){
  
  print("Preparing exportation into BDD...")
  
  # PREPROCESS DATA pour export en bdd
  setnames(dt_emission, c('emission amount  (=concentration as reported)', 'detect - non-detect flag'), 
           c('emission_amount_concentration_as_reported', 'detect_non_detect_flag'))
  names(dt_emission) <- gsub(" ", "_", names(dt_emission))
  
  
  # Export data to database 
  t_tmp <- Sys.time()
  tryCatch(
    {
      dbCon <- dbConnect(PostgreSQL(),
                         host = DB_HOST,
                         dbname = DB_NAME,
                         user = DB_USER,
                         password = DB_PASSWORD)
      
      print(paste0("Exporting data into ", table_epa_emission,"..."))
      dbWriteTable(dbCon, table_epa_emission, dt_emission, overwrite=TRUE, row.names=FALSE)
      
      dbDisconnect(dbCon)
      
      print(paste0("End of exporting results. Time spent: ",
                   round(difftime(Sys.time(), t_tmp, units = "secs"), 2), " secondes"))
      
    },
    
    error = function(cond) {
      message(paste("Error in exporting data."))
      message("Here is the original error message:")
      message(cond)
      message()
      dbDisconnect(dbCon)
      return(NULL)
    }
  )
  
  
}


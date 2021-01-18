
library(data.table)
library(readxl)

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
file_transco <- "transco_variables_v5.xlsx"

date_today <- format(Sys.Date(), format="%Y%m%d")

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

# Supprimer les lignes full NA
dt_total[, is_na := rowSums(is.na(dt_total))==13]
dt_total <- dt_total[!is_na==TRUE]
dt_total[,is_na:=NULL]
# Supprimer les lignes avec et emission amount facility null
dt_total <- dt_total[!(is.na(facility) & is.na(`emission amount  (=concentration as reported)`))]
# Supprimer les lignes correspondant aux run id "1-O-M23-1" et "2-O-M23-1" 
# car on retrouve systématiquement plusieurs valeurs différentes par échantillon
dt_total <- dt_total[! `run id` %in% c("1-O-M23-1", "2-O-M23-1")]

# Mettre les concentrations en numérique
## changer les ".." en "." (1 ligne à défaut ds MWI-LAST/MWIMAJOR.XLS pour la substance 5F Other)
dt_total[, `emission amount  (=concentration as reported)`:=gsub("\\..", ".", `emission amount  (=concentration as reported)`)]
## 
dt_total[,`emission amount  (=concentration as reported)`:=as.double(`emission amount  (=concentration as reported)`)]
dt_total <- dt_total[!(is.na(`emission amount  (=concentration as reported)`))]


# Charger les matrices de transco pour corriger 
dt_substance <- as.data.table(read_excel(paste0(folder_output, "\\", file_transco), sheet='transco_substance'))
dt_conso <- as.data.table(read_excel(paste0(folder_output, "\\", file_transco), sheet='transco_concentration'))
dt_detect <- as.data.table(read_excel(paste0(folder_output, "\\", file_transco), sheet='transco_detect'))
dt_categ <- as.data.table(read_excel(paste0(folder_output, "\\", file_transco), sheet='transco_category'))

# jointure avec les tables de transco pour modifier les modalités
dt_total <- merge(dt_total, dt_substance[, .(substance, proposition, keep)], 
                  by='substance', all.x=TRUE, all.y=FALSE)
dt_total <- dt_total[keep=='yes',]
dt_total[,":="(substance=proposition, keep=NULL)]
dt_total[,proposition:=NULL]

dt_total <- merge(dt_total, dt_conso[, .(`concentration units as reported`, proposition, concentration_unit, gaz_rate)], 
                  by="concentration units as reported", all.x=TRUE, all.y=FALSE)
dt_total[,":="(`concentration units as reported`=proposition)]
dt_total[,proposition:=NULL]

dt_total <- merge(dt_total, dt_detect[, .(`detect - non-detect flag`, proposition, keep)], 
                  by='detect - non-detect flag', all.x=TRUE, all.y=FALSE)
dt_total <- dt_total[keep=='yes',]
dt_total[,":="(`detect - non-detect flag`=proposition)]
dt_total[,proposition:=NULL]

dt_total <- merge(dt_total, dt_categ[, .(`source category`, `source subcategory`, proposition_category, proposition_subcategory)], 
                  by=c("source category", "source subcategory"), all.x=TRUE, all.y=FALSE)
dt_total[,":="(`source category` = proposition_category, `source subcategory` = proposition_subcategory)]
dt_total[,":="(proposition_category=NULL, proposition_subcategory=NULL)]


# reordonner les colonnes
dt_total <- dt_total[,.(`epa id number`, facility, city, state, `release media`, `run id`, `test date`, 
                        file, `source category`, `source subcategory`, substance, `detect - non-detect flag`,
                        `emission amount  (=concentration as reported)`, `concentration units as reported`,
                        concentration_unit, gaz_rate)]


# Export de la base en csv
write.csv2(dt_total, file=paste0(folder_output, "base_emission_dioxdb_", date_today, ".csv"))






# #############################################
# # EXTRACTION DES MATRICES DE TRANSCO
# #############################################
# # Cleaning et regroupement de variables
# dt_detect <- dt_total[,.N, `detect - non-detect flag`]
# dt_substance <- dt_total[,.N, substance]
# dt_concentration <- dt_total[,.N, `concentration units as reported`]
# dt_category <- dt_total[,.N,.(`source category`, `source subcategory`)]
# 
# ##Initialisation
# dt_detect[,":="(proposition=`detect - non-detect flag`)]
# dt_substance[,":="(proposition=substance)]
# dt_concentration[, ":="(proposition=`concentration units as reported`)]
# dt_category[,":="(proposition=`source subcategory`)]
# 
# dt_substance <- dt_substance[order(substance)]
# dt_category <- dt_category[order(`source category`, `source subcategory`)]
# 
# ## Export 
# write.csv2(dt_detect, file=paste0(folder_output, "transco_detect.csv"))
# write.csv2(dt_substance, file=paste0(folder_output, "transco_substance.csv"))
# write.csv2(dt_concentration, file=paste0(folder_output, "transco_concentration.csv"))
# write.csv2(dt_category, file=paste0(folder_output, "transco_category.csv"))
# #############################################



# # Analyse de la base
# summary(dt_total)
# 
# colSums(sapply(dt_total, is.na))







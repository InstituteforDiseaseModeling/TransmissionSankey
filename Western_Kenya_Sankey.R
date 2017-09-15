
#library('reshape2')
library('googleVis')
library('stringr')

NonResident_base_dir = '../run_NonResident/NonResident Baseline SQ SANKEY/Nyanza NonResident SQ Baseline Resample 826/'
Resident_base_dir =    '../run_Resident/Resident Baseline SQ SANKEY/Nyanza Resident SQ Baseline Resample 826/'

curr_base_dir <- Resident_base_dir
transmission_gender <- 'M_to_F'

## import contingency table of SRC_Risk vs DEST_Risk
curr_filename = 'SRC_Risk_vs_DEST_Risk'

data_imported = read.csv(paste(curr_base_dir,curr_filename,'/',curr_filename,'_TPI0000_REP0001.csv',sep=''))
data_colnames = colnames(data_imported)
FROM_colname <- data_colnames[1] 
data_colnames <- data_colnames[2:length(data_colnames)]

for(TPI_iter in 1:249){
    data_to_add = read.csv(paste(curr_base_dir,curr_filename,'/',curr_filename,'_TPI',str_pad(toString(TPI_iter), 4, pad = "0"),'_REP0001.csv',sep=''))    
    for(colname in data_colnames){
        if(colname %in% colnames(data_to_add)){data_imported[colname] <- data_imported[colname] + data_to_add[colname]}
        }
        
    }

for(colname in data_colnames){
    data_imported[colname] <- data_imported[colname]/5 # div 250 reps by 5 to get pop scaling of ~50
}


row.names(data_imported)<- as.vector(data_imported[,FROM_colname])
data_imported[,FROM_colname] <- NULL
data_ctable = as.table(as.matrix(data_imported))
data_df <- as.data.frame(data_ctable)
data_df$From <- data_df$Var1
data_df$Var1 <- NULL
data_df$To <- data_df$Var2
data_df$Var2 <- NULL

data_df$From <- paste(tolower(data_df$From),'-risk transmitter',sep='')
#data_df<-data_df[order(factor(data_df$From,levels=c('low-risk transmitter','medium-risk transmitter','high-risk transmitter'))),]

data_df$To <- paste(tolower(data_df$To),'-risk recipient',sep='')
#data_df<-data_df[order(factor(data_df$To,  levels=c('low-risk recipient','medium-risk recipient','high-risk recipient'))),]


sankey_df <- data_df

## Import contingency of DEST_Risk vs. Node ID

curr_filename = 'DEST_Risk_vs_NODE_ID'

data_imported = read.csv(paste(curr_base_dir,curr_filename,'/',curr_filename,'_TPI0000_REP0001.csv',sep=''))
data_colnames = colnames(data_imported)
FROM_colname <- data_colnames[1] 
data_colnames <- data_colnames[2:length(data_colnames)]

for(TPI_iter in 1:249){
    data_to_add = read.csv(paste(curr_base_dir,curr_filename,'/',curr_filename,'_TPI',str_pad(toString(TPI_iter), 4, pad = "0"),'_REP0001.csv',sep=''))    
    for(colname in data_colnames){
        if(colname %in% colnames(data_to_add)){data_imported[colname] <- data_imported[colname] + data_to_add[colname]}
    }
    
}

for(colname in data_colnames){
    data_imported[colname] <- data_imported[colname]/5 # div 250 reps by 5 to get pop scaling of ~50
}


row.names(data_imported)<- as.vector(data_imported[,FROM_colname])
data_imported[,FROM_colname] <- NULL
data_ctable = as.table(as.matrix(data_imported))
data_df <- as.data.frame(data_ctable)
data_df$From <- data_df$Var1
data_df$Var1 <- NULL
data_df$To <- data_df$Var2
data_df$Var2 <- NULL

data_df$From <- paste(tolower(data_df$From),'-risk recipient',sep='')
#data_df<-data_df[order(factor(data_df$From,  levels=c('low-risk recipient','medium-risk recipient','high-risk recipient'))),]
#data_df<-data_df[order(factor(data_df$To,  levels=c('Siaya','Homa Bay','Kisumu','Migori','Nyamira','Kisii'))),]
sankey_df <- rbind(sankey_df,data_df)


levels(sankey_df$From) <- c()


# Import contingency table of NODE_ID vs SRC_Risk

curr_filename = 'NODE_ID_vs_SRC_Risk'

data_imported = read.csv(paste(curr_base_dir,curr_filename,'/',curr_filename,'_TPI0000_REP0001.csv',sep=''))
data_colnames = colnames(data_imported)
FROM_colname <- data_colnames[1] 
data_colnames <- data_colnames[2:length(data_colnames)]

for(TPI_iter in 1:249){
    data_to_add <- read.csv(paste(curr_base_dir,curr_filename,'/',curr_filename,'_TPI',str_pad(toString(TPI_iter), 4, pad = "0"),'_REP0001.csv',sep=''))    
    data_imported <- aggregate(. ~ NODE_ID, rbind(data_imported,data_to_add), sum)

    
}

for(colname in data_colnames){
    data_imported[colname] <- data_imported[colname]/5 # div 250 reps by 5 to get pop scaling of ~50
}

# to do: average

row.names(data_imported)<- as.vector(data_imported[,FROM_colname])
data_imported[,FROM_colname] <- NULL
data_ctable = as.table(as.matrix(data_imported))
data_df <- as.data.frame(data_ctable)
data_df$From <- data_df$Var1
data_df$Var1 <- NULL
data_df$To <- data_df$Var2
data_df$Var2 <- NULL

data_df$To <- paste(tolower(data_df$To),'-risk transmitter',sep='')
#data_df<-data_df[order(factor(data_df$To,  levels=c('low-risk transmitter','medium-risk transmitter','high-risk transmitter'))),]


sankey_df <- rbind(sankey_df,data_df)

# reorder columns. Sankey package needs first column to be a string.
sankey_df <- sankey_df[,c(2, 3, 1)]

sankey_df$From[sankey_df$From==1] <- 'Homa Bay'
sankey_df$From[sankey_df$From==2] <- 'Kisii'
sankey_df$From[sankey_df$From==3] <- 'Kisumu'
sankey_df$From[sankey_df$From==4] <- 'Migori'
sankey_df$From[sankey_df$From==5] <- 'Nyamira'
sankey_df$From[sankey_df$From==6] <- 'Siaya'

sankey_df$To[sankey_df$To=='X1'] <- 'Homa Bay '
sankey_df$To[sankey_df$To=='X2'] <- 'Kisii '
sankey_df$To[sankey_df$To=='X3'] <- 'Kisumu '
sankey_df$To[sankey_df$To=='X4'] <- 'Migori '
sankey_df$To[sankey_df$To=='X5'] <- 'Nyamira '
sankey_df$To[sankey_df$To=='X6'] <- 'Siaya '


sankey_df$From[sankey_df$From=='high-risk transmitter'] <- "high-risk tr."
sankey_df$From[sankey_df$From=='high-risk recipient'] <- "high-risk rec."
sankey_df$To[sankey_df$To=='high-risk transmitter'] <- "high-risk tr."
sankey_df$To[sankey_df$To=='high-risk recipient'] <- "high-risk rec."


sankey_df<-sankey_df[order(factor(sankey_df$From,  levels=c('Siaya','Homa Bay','Kisumu','Migori','Nyamira','Kisii','high-risk tr.','medium-risk transmitter','low-risk transmitter','high-risk rec.','medium-risk recipient','low-risk recipient'))),]
sankey_df<-sankey_df[order(factor(sankey_df$To,  levels=c('Siaya ','Homa Bay ','Kisumu ','Migori ','Nyamira ','Kisii ','high-risk tr.','medium-risk transmitter','low-risk transmitter','high-risk rec.','medium-risk recipient','low-risk recipient'))),]

plot(
    gvisSankey(sankey_df,
               from="FROM", 
               to="TO", weight="Freq",
               options=list(
                   height=250,
                   sankey="{iterations:0,link:{color:{fill:'lightblue'}},node:{color:{fill:'blue'}}}"
               ))
)


# 
# plot(
#     gvisSankey(sankey_df,
#                from="FROM", 
#                to="TO", weight="Freq",
#                options=list(
#                    height=250,
#                    sankey="{iterations:0,link:{color:{fill:'lightblue'}}}"
#                ))
# )
# 

# sankey="{iterations:0,link:{color:{fill:'lightblue'}},node:{ color: { fill: '#a61d4c' }}}"

## Sankey with crazy colors

#plot(
#  gvisSankey(sankey_df,
#             from="FROM", 
#             to="TO", weight="Freq",
#             options=list(
#               height=250,
#               sankey="{link:{colorMode:'gradient'}}"
 #            ))
#)

#options = {
#  height: 400,
#  sankey: {
#    node: {
#      colors: colors
#    },
#    link: {
#      colorMode: 'gradient',
#      colors: colors
#    }
#  }
#


#link: {
#  colorMode: 'gradient',
#  colors: colors
#}

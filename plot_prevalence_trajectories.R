library('stringr')
library(plyr)
library(reshape2)
library(lattice)
library(latticeExtra)

NonResident_base_dir = 'Nyanza NonResident SQ Baseline Resample 826/'
Resident_base_dir =    'Nyanza Resident SQ Baseline Resample 826/'
first_plot = T

curr_base_dir <- Resident_base_dir
curr_filename = 'ReportHIVByAgeAndGender'


#data_imported = read.csv(paste(curr_base_dir,curr_filename,'/',curr_filename,'_TPI0000_REP0001.csv',sep=''))


for(TPI_iter in 0:10){

data_imported = read.csv(paste(curr_base_dir,curr_filename,'/',curr_filename,'_TPI',str_pad(toString(TPI_iter), 4, pad = "0"),'_REP0001.csv',sep=''))    
    

data_imported <- as.data.frame(data_imported)

data_imported <- data_imported[data_imported$Age>=15 & data_imported$Age<50 &  data_imported$Year > 1995 & data_imported$Year < 2018.5,]
data_imported <- aggregate( cbind(Population, Infected) ~ Year + NodeId + Gender, data=data_imported, FUN=sum)
data_imported$Prevalence = data_imported$Infected/data_imported$Population
data_imported$Population <- NULL
data_imported$Infected <- NULL


data_imported$NodeId = as.factor( data_imported$NodeId  )
data_imported$NodeId = revalue( data_imported$NodeId, c(
    "1" = "Homa Bay",
    "2" = "Kisii",
    "3" = "Kisumu",
    "4" = "Migori",
    "5" = "Nyamira",
    "6" = "Siaya") )

data_imported$Gender = as.factor( data_imported$Gender  )
data_imported$Gender = revalue( data_imported$Gender, c(
    "0" = "Male",
    "1" = "Female") )

data_imported$Gender <- factor(data_imported$Gender, levels = c('Female','Male'))
data_imported$NodeId <- factor(data_imported$NodeId, levels = c('Kisii','Nyamira','Migori','Kisumu','Homa Bay','Siaya'))

#levels(data_imported$Gender) <- c('Female','Male')
#levels(data_imported$NodeId) <- c('Siaya','Homa Bay','Kisumu','Migori','Nyamira','Kisii')
#data_imported$NodeId = as.factor( data_imported$NodeId  )
#levels(data_imported$NodeId) <- c('Kisii','Nyamira','Migori','Kisumu','Homa Bay','Siaya') #custom factor order

#data_wide <-  cast(data_imported, Year + Gender ~ NodeId, value='Prevalence', fill=FALSE)

plot_to_add <- xyplot(Prevalence~Year | factor(Gender) + factor(NodeId),
  data=data_imported,  
  xlab="Year", ylab="Prevalence",pch=19,type=c("l"),ylim=c(0, .5))

if(first_plot == T){curr_plot = plot_to_add; first_plot=F} else{curr_plot = curr_plot + as.layer(plot_to_add)}
print(paste('Plotted TPI number ', toString(TPI_iter + 1),sep=''))

}


pt_f <- read.csv('Female_prev_point.csv')    
pt_f$Year <- pt_f$X
pt_f$X <- NULL
pt_f['Homa Bay'] <- pt_f$Homa.Bay
pt_f$Homa.Bay <- NULL
pt_f$Gender <- 'Female'

pt_m <- read.csv('Male_prev_point.csv')    
pt_m$Year <- pt_m$X
pt_m$X <- NULL
pt_m['Homa Bay'] <- pt_m$Homa.Bay
pt_m$Homa.Bay <- NULL
pt_m$Gender <- 'Male'

prev_wide <- rbind(pt_f, pt_m)


prev_long <- melt(prev_wide,id.vars = c("Year", "Gender"), variable.name = 'NodeId', value.name = 'Prevalence')
prev_long <- as.data.frame(prev_long)

# not sure why the options didn't work
#prev_long$NodeId <- prev_long$variable
#prev_long$variable <- NULL
#prev_long$Prevalence <- prev_long$value
#prev_long$value <- NULL
#prev_long<-prev_long[order(factor(prev_long$NodeId,  levels=c('Siaya','Homa Bay','Kisumu','Migori','Nyamira','Kisii','high-risk tr.','medium-risk transmitter','low-risk transmitter','high-risk rec.','medium-risk recipient','low-risk recipient'))),]



prev_long$Gender <- factor(prev_long$Gender, levels = c('Female','Male'))
prev_long$NodeId <- factor(prev_long$NodeId, levels = c('Kisii','Nyamira','Migori','Kisumu','Homa Bay','Siaya'))

#levels(prev_long$Gender) <- c('Female','Male')
#levels(prev_long$NodeId) <- c('Kisii','Nyamira','Migori','Kisumu','Homa Bay','Siaya') #custom factor order

plot_to_add <- xyplot(Prevalence~Year | factor(Gender) + factor(NodeId),
                      data=prev_long,  
                      xlab="Year", ylab="Prevalence",pch=19,type=c("p"),par.settings=simpleTheme(col="black"),ylim=c(0, .5))
# see http://www.martin-elff.net/knitr/memisc/errbars.html 
saved_plot = curr_plot

curr_plot = curr_plot + as.layer(plot_to_add)

#curr_plot
#curr_plot = saved_plot

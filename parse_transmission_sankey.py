
## Sankey figures:
# 2 panels for L/M/H transmitters to L/M/H recipients: 15-49 F, 15-49 M.
# 4 panels for SI: 15-24 F, 15-24 M, 25-49 F, 25-49 M
# 2 panels for male -> female and female -> male transmitter/recipient pairs, in 5 year age bins 
# for SI: all of the above, stratified by county

## Format of data table for Sankey, from transmissions 2015-2020 (with merged-in data on IPs)

# Node recoded to County
# Gender
# Age in 5-year strata

# --> derive Age in 15-24 or 25-49 or not
# --> derive Age 15-49 or not


# Number of acquired infections
# Number of transmitted infections


## define Sankey categories

# Age ranges: <15, 15-24, 25-49, 50+
# Gender: M, F
# Risk group: L, M, H
# (Less relevant) -- relationship type: T, I, M, C (check if commercial was added to Rel_type enum)

## read in transmission.csv, discard rows except in the years of interest, 2015-2020

## for each row of interest, look up IP list of A from RelationshipStart.csv



import pandas as pd
import os as os
import time as time
#from os import listdir
#from os import path

curr_folder = 'output_TRANSMISSION_AND_RELATIONSHIPS'
base_directory_path = 'Z:/mint/Dropbox (IDM)/research/HIV/2017/Kenya_non_resident_comparison/modeling'


script_start_time = time.time()


# load transmission report  as a pandas data frame
transm = pd.read_csv(os.path.join(base_directory_path, curr_folder, 'TransmissionReport.csv'))
#print(transm.shape)

# keep only years >=2015 and <2020
transm = transm[(transm.YEAR >= 2015) & (transm.YEAR < 2020)]
# print(transm.shape) # down to a few thousand transmission events
    

# drop irrelevant columns
# print(transm.columns.values)
transm = transm[['YEAR','NODE_ID','SRC_ID','SRC_GENDER','SRC_AGE','SRC_CIRCUMSIZED','SRC_INF_AGE', 'DEST_ID','DEST_GENDER','DEST_AGE','DEST_CIRCUMSIZED']]
# print(transm.shape)


# load relationship CSV
rels = pd.read_csv(os.path.join(base_directory_path, curr_folder, 'RelationshipStart.csv'))

# print(rels.shape)
# print(list(rels)) #same as print(rels.columns.values)
rels = rels[['Rel_start_time','Rel_type (0 = TRANSITORY; 1 = INFORMAL; 2 = MARITAL; 3 = COMMERCIAL)','Current_node_ID', 'A_ID', 'B_ID', 'A_IndividualProperties', 'B_IndividualProperties']]
rels['YEAR'] = rels.Rel_start_time/365 + 1960.5
rels = rels[(rels.YEAR  < 2020)]

transm['Risk'] = 'TBD'

# for each transmission event in 2015-2020,
for transm_index, curr_transm in transm.iterrows():
   
    print(transm_index)    
    if transm_index%100 == 0:
        iter_start_time = time.time()
    # take the FROM individual ID and year of transmission event
    curr_FROM_ID = curr_transm['SRC_ID']
    curr_transm_yr = curr_transm['YEAR']
    SRC_rels = rels[((rels.A_ID == curr_transm['SRC_ID']) | (rels.B_ID == curr_transm['SRC_ID']))]
    
    # determine if they have been in a COMMERCIAL relship prior to the date of transmission:
    SRC_commercial_rels = SRC_rels[(SRC_rels['Rel_type (0 = TRANSITORY; 1 = INFORMAL; 2 = MARITAL; 3 = COMMERCIAL)']==3) & (SRC_rels['YEAR'] <= curr_transm_yr)]

    if SRC_commercial_rels.shape[0]>0:
      #  transm.Risk.loc[[transm_index]] = 'HIGH'
      transm.set_value(transm_index,'Risk','HIGH')
    else:
    
        # the SRC transmitter could be either person A or person B in the relationship. 
        # If they are person A and person A's Individual Properties are Risk-MEDIUM, then they are MEDIUM risk. Call this Condition A.
        condition_A_to_be_MEDIUM_Risk = sum((rels.A_ID == curr_transm['SRC_ID']) & (SRC_rels.A_IndividualProperties.str.contains("MEDIUM")))>0
        
        # If they are person B and person B's Individual Properties are Risk-MEDIUM, then they are MEDIUM risk. Call this Condition B.
        condition_B_to_be_MEDIUM_Risk = sum((rels.B_ID == curr_transm['SRC_ID']) & (SRC_rels.B_IndividualProperties.str.contains("MEDIUM")))>0
        
        if condition_A_to_be_MEDIUM_Risk | condition_B_to_be_MEDIUM_Risk:
            #transm.Risk.loc[[transm_index]] = 'MEDIUM'
            transm.set_value(transm_index,'Risk','MEDIUM')
        else:
            #transm.Risk.loc[[transm_index]] = 'LOW'
             transm.set_value(transm_index,'Risk','LOW')
    if transm_index%100 == 0:
        print("100 transmissions up to %d took %f seconds" % (transm_index, time.time() - iter_start_time))
   

# repeat for TO individual.

# --- not yet FSW/client --- currently FSW/client --- no longer FSW/client ---
# if transmission happens any time after "currently FSW", consider it to come from a FSW
# because that person would report that they have previously exchanged $ for FSW


# check how long it took to do one dataset
print("Total script runtime was %f seconds" % (time.time() - script_start_time))


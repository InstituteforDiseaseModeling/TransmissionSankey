
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
save_transmission_dataset_filename = "Transmission_with_RiskIP.pkl"
how_often_to_report_time = 1 # number of transmission events to record before reporting time

script_start_time = time.time()
progress_tracker = 0


# load transmission report  as a pandas data frame
transm = pd.read_csv(os.path.join(base_directory_path, curr_folder, 'TransmissionReport.csv'))

# keep only years >=2015 and <2020
transm = transm[(transm.YEAR >= 2015) & (transm.YEAR < 2020)]

# keep only relevant columns
transm = transm[['YEAR','NODE_ID','SRC_ID','SRC_GENDER','SRC_AGE','SRC_CIRCUMSIZED','SRC_INF_AGE', 'DEST_ID','DEST_GENDER','DEST_AGE','DEST_CIRCUMSIZED']]

transm = transm.head(10)

#global rels
#global number_of_transmissions_to_analyze
number_of_transmissions_to_analyze = transm.shape[0]

# load relationship CSV
rels = pd.read_csv(os.path.join(base_directory_path, curr_folder, 'RelationshipStart.csv'))

# keep only relevant columns
rels = rels[['Rel_start_time','Rel_type (0 = TRANSITORY; 1 = INFORMAL; 2 = MARITAL; 3 = COMMERCIAL)','Current_node_ID', 'A_ID', 'B_ID', 'A_IndividualProperties', 'B_IndividualProperties']]

# the model logs time only in days. Translate this to years using 1960.5 as Start_Year
# Note, verify that this Start_Year is correct by checking config.json
rels['YEAR'] = rels.Rel_start_time/365 + 1960.5
rels = rels[(rels.YEAR  < 2020)]

#transm['SRC_Risk'] = 'SRC_TBD'
#transm['DEST_Risk'] = 'DEST_TBD'

# for each transmission event in 2015-2020,
def determine_risk_IP_for_SRC(curr_transm):
     
    iter_start_time = time.time()
    global progress_tracker 
    global script_start_time
    global rels
    global number_of_transmissions_to_analyze
    
    # take the FROM individual ID and year of transmission event
    curr_SRC_ID = curr_transm['SRC_ID']
    curr_transm_yr = curr_transm['YEAR']
    
    
    # assign IP to SRC individual
    
    SRC_rels = rels[((rels.A_ID == curr_SRC_ID) | (rels.B_ID == curr_SRC_ID))]
    
    # determine if they have been in a COMMERCIAL relship prior to the date of transmission:
    SRC_commercial_rels = SRC_rels[(SRC_rels['Rel_type (0 = TRANSITORY; 1 = INFORMAL; 2 = MARITAL; 3 = COMMERCIAL)']==3) & (SRC_rels['YEAR'] <= curr_transm_yr)]

    if SRC_commercial_rels.shape[0]>0:
      #  transm.SRC_Risk.loc[[transm_index]] = 'HIGH'
      #  transm.set_value(transm_index,'SRC_Risk','HIGH')
      curr_Risk = 'HIGH'
    else:
    
        # the SRC transmitter could be either person A or person B in the relationship. 
        # If they are person A and person A's Individual Properties are Risk-MEDIUM, then they are MEDIUM risk. Call this Condition A.
        condition_A_to_be_MEDIUM_Risk = sum((rels.A_ID == curr_SRC_ID) & (SRC_rels.A_IndividualProperties.str.contains("MEDIUM")))>0
        
        # If they are person B and person B's Individual Properties are Risk-MEDIUM, then they are MEDIUM risk. Call this Condition B.
        condition_B_to_be_MEDIUM_Risk = sum((rels.B_ID == curr_SRC_ID) & (SRC_rels.B_IndividualProperties.str.contains("MEDIUM")))>0
        
        if condition_A_to_be_MEDIUM_Risk | condition_B_to_be_MEDIUM_Risk:
            #transm.SRC_Risk.loc[[transm_index]] = 'MEDIUM'
            #transm.set_value(transm_index,'SRC_Risk','MEDIUM')
            curr_Risk = 'MEDIUM'
        else:
            #transm.SRC_Risk.loc[[transm_index]] = 'LOW'
            #transm.set_value(transm_index,'SRC_Risk','LOW')
             curr_Risk = 'LOW'
        
        progress_tracker = progress_tracker + 0.5
        cumulative_percent_complete = (100*progress_tracker/number_of_transmissions_to_analyze)
        computation_time_so_far = time.time() - script_start_time
        estimated_total_computation_time = computation_time_so_far/(cumulative_percent_complete/100)
        estimated_remaining_computation_time = estimated_total_computation_time*((100-cumulative_percent_complete)/100)
        
        
        print("Current SRC took %f seconds" % ( time.time() - iter_start_time))  
        print("Analysis is %f percent complete" % cumulative_percent_complete)  
        print("Estimated remaining time is %f seconds or %f hours" % (estimated_remaining_computation_time, estimated_remaining_computation_time/60/60))  
        return curr_Risk
    

def determine_risk_IP_for_DEST(curr_transm):

    iter_start_time = time.time()
    global progress_tracker 
    global script_start_time
    global rels
    global number_of_transmissions_to_analyze
    
    curr_DEST_ID = curr_transm['DEST_ID']    
    # assign IP to DEST individual
    
    DEST_rels = rels[((rels.A_ID == curr_DEST_ID) | (rels.B_ID == curr_DEST_ID))]
    
    # determine if they have been in a COMMERCIAL relship prior to the date of transmission:
    DEST_commercial_rels = DEST_rels[(DEST_rels['Rel_type (0 = TRANSITORY; 1 = INFORMAL; 2 = MARITAL; 3 = COMMERCIAL)']==3) & (DEST_rels['YEAR'] <= curr_transm_yr)]

    if DEST_commercial_rels.shape[0]>0:
      #  transm.DEST_Risk.loc[[transm_index]] = 'HIGH'
      # transm.set_value(transm_index,'DEST_Risk','HIGH')
      curr_Risk = 'HIGH'
    else:
    
        # the DEST transmitter could be either person A or person B in the relationship. 
        # If they are person A and person A's Individual Properties are Risk-MEDIUM, then they are MEDIUM risk. Call this Condition A.
        condition_A_to_be_MEDIUM_Risk = sum((rels.A_ID == curr_DEST_ID) & (DEST_rels.A_IndividualProperties.str.contains("MEDIUM")))>0
        
        # If they are person B and person B's Individual Properties are Risk-MEDIUM, then they are MEDIUM risk. Call this Condition B.
        condition_B_to_be_MEDIUM_Risk = sum((rels.B_ID == curr_DEST_ID) & (DEST_rels.B_IndividualProperties.str.contains("MEDIUM")))>0
        
        if condition_A_to_be_MEDIUM_Risk | condition_B_to_be_MEDIUM_Risk:
            #transm.DEST_Risk.loc[[transm_index]] = 'MEDIUM'
            #transm.set_value(transm_index,'DEST_Risk','MEDIUM')
            curr_Risk = 'MEDIUM'
        else:
            #transm.DEST_Risk.loc[[transm_index]] = 'LOW'
            #transm.set_value(transm_index,'DEST_Risk','LOW')     
            curr_Risk = 'LOW'             
             
        progress_tracker = progress_tracker + 0.5
        cumulative_percent_complete = (100*progress_tracker/number_of_transmissions_to_analyze)
        computation_time_so_far = time.time() - script_start_time
        estimated_total_computation_time = computation_time_so_far/(cumulative_percent_complete/100)
        estimated_remaining_computation_time = estimated_total_computation_time*((100-cumulative_percent_complete)/100)
        
        
        print("Current SRC took %f seconds" % ( time.time() - iter_start_time))  
        print("Analysis is %f percent complete" % cumulative_percent_complete)  
        print("Estimated remaining time is %f seconds or %f hours" % (estimated_remaining_computation_time, estimated_remaining_computation_time/60/60)) 
        return curr_Risk
   

transm['SRC_Risk'] = transm.apply(determine_risk_IP_for_SRC, axis=1)
transm['DEST_Risk'] = transm.apply(determine_risk_IP_for_DEST, axis=1)

# check how long it took to do one dataset
print("Total script runtime was %f seconds" % (time.time() - script_start_time))

print("Saving IP cross-referenced transmission dataset to filename " + save_transmission_dataset_filename)
transm.to_pickle(save_transmission_dataset_filename)  # where to save it, usually as a .pkl

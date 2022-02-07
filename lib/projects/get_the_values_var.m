%import_data = readmatrix('SNL_18650_NMC_25C_0-100_0.5-1C_b_timeseries.csv');
%import_data = readmatrix('HNEI_18650_NMC_LCO_25C_0-100_0.5-1.5C_b_timeseries.csv');

%import_data = readmatrix('OX_1-1_pouch_LCO_40C_0-100_2-1.84C_a_timeseries.csv');
%import_data = readmatrix('HNEI_18650_NMC_LCO_25C_0-100_0.5-1.5C_t_timeseries.csv');
function [drv_tran,not_test_cycles, test_cycles, dis_cap, char_cap, Ntime_d, Ntime_c, Ntime_cv_char] = get_the_values_var(import_data)

currents = import_data(:,4);    
volts = import_data(:,5);      
time_v = import_data(:,2);  

[pks,locs] = findpeaks(-volts);


%% plot the voltage of the whole trial
% % this is a debuggng feature so you can check what the voltage and current
% % looks like
figure
plot(time_v(1:10000),volts(1:10000))
title('Voltage')
xlabel('time')

hold on

plot(time_v(1:10000), currents(1:10000))
title('Current and voltage')

ylabel('current or voltage')

%% find the minimums or valleys of the voltage signal 
%  get the min values: newpks at newlocs
%  use the find peaks and take negative to get valleys
 pks =-pks;
 temp = pks < 3.1;
 newpks = pks(temp);   % create a truth vector, eleminate false mins

 newlocs = locs(temp);  % locs are indecies not times
 time_locs = time_v(newlocs);  % get the time the mins occur
                                %%% if you want a figure uncomment the
                                %%% peice below
 figure
 scatter(time_locs, newpks)
 title('time of minima')
 xlabel('time')
 ylabel('voltage')
 


%___________
%%% find the length time of the zero to zero cycle store it in 'gaps'
%%% find the actual indices vallue of the zero to zero cycle store it in
%%% ind_gaps

gaps = zeros(1,length(time_locs));
ind_gaps = gaps;
for i = 1:length(time_locs)-1 
     gaps(i+1) = time_locs(i+1)- time_locs(i) ; %get the time gaps
     ind_gaps(i+1)= newlocs(i+1)- newlocs(i) ;   % get the indeces
end
 
gaps(1)= time_locs(1);
ind_gaps(1) = newlocs(1);
cap_test = zeros(1, length(volts));
cap_counter = 1;
  
 %% identify and count capacitance tests
 
% we want to start isolateing the capacitance test/check cycles from other cycles
% One identifying portion will be the max current during a cycle we store this value 
% in ' avgMaxCur'. We then set a trigger based on the average max current
% value. The capacitance check/test cycles should have lower than average
% currents.


 avgMaxCur= zeros(1,length(time_locs)); % same as length of gaps
 for j=1: length(gaps)
       tmp_v= volts(cap_counter: (cap_counter + ind_gaps(j)-1));
       [m, i] = max(tmp_v);
       tmp_c= currents((cap_counter + i): (cap_counter + ind_gaps(j)-1));
       
       avgMaxCur(j) = max(abs(tmp_c));
       cap_counter = cap_counter + ind_gaps(j);  %ticking through the array
  end
avg_Cur = sum(avgMaxCur)/(length(gaps));
triger= mean(avgMaxCur)*0.6 

% count how many tests are cap checks in 'num_test' . We assume all are
% then subtract if it fails trigger.

 num_tests = length(gaps);
 cap_counter = 1;
wher_cap = ones(1, length(ind_gaps));
 for j=1: length(gaps)%-1
   if avgMaxCur(j)> (triger) %|(gaps(j) < mean(gaps(j)))
       num_tests = num_tests-1;
       wher_cap(j)= 0;
   end
 end
 
 % Now we engineer for common corner cases. Some data files have all test
 % cycles so we say if we find fewer than 6 test cycles. then all of them
 % must be test cycles.
 
 if(num_tests>6)
 test_cycles = find(wher_cap);
 not_testcycles = find(~wher_cap);
 end
 
 if(num_tests<=6)
 test_cycles = 1:length(avgMaxCur);
 not_testcycles = zeros(1, length(avgMaxCur));
 triger = 1.1*max(avgMaxCur);
 num_tests = length(avgMaxCur);
 end
 
 
 %%%identify and store the cap checks/test cycles in a matrix
 cap_test_mat = zeros(num_tests, max(ind_gaps),3);
 num_test_count= 0;
 
     % grab the voltages that are the cap tests
     % create the matrix with the cap tests
    cap_counter = 1;
   for j=1: length(gaps)%-1
    if avgMaxCur(j)< (triger)% & (gaps(j) > mean(gaps(j)))
        cap_test(cap_counter: (cap_counter + ind_gaps(j)-1))= volts(cap_counter: (cap_counter + ind_gaps(j)-1));
        num_test_count= num_test_count+1;
        cap_test_mat(num_test_count,1:ind_gaps(j),1)= volts(cap_counter: (cap_counter + ind_gaps(j)-1))';
        cap_test_mat(num_test_count,1, 2) = cap_counter;
        cap_test_mat(num_test_count,1, 3) = cap_counter + ind_gaps(j)-1;
    end
   
    cap_counter = cap_counter + ind_gaps(j);  %ticking through the array
   end
   
   
   %so now all the cap test/check cycles are stored in a mat 'cap_test_mat'
 
 cut_off = cap_test> min(volts);
 new_cap_test= cap_test(cut_off);
 time_cut = time_v(cut_off);
  
% debugging plots
  figure

  plot( cap_test)
  title('cap test')
  xlabel('indeces')
  ylabel('voltage')
  
   
%   figure      
%   for i = 1:length(cap_test_mat(:,1,1))
%       plt_len = cap_test_mat(i,1,3)- cap_test_mat(i,1,2) +1 ;
%       plot(time_v(cap_test_mat(i,1,2):cap_test_mat(i,1,3)),cap_test_mat(i,1:plt_len,1))
%       hold on
%   end
  


 %% discharge matrix
 % create two matrix from the test cap mat matrix that holds the
 % discharge discharge portion of the cycle. one mat for voltage one for
 % current. We start by identifing the maximum voltage value of the cycle
 % and then we determine where the discharge beggins with the current and
 % volage gradient
 
 
 dis_mat_v = zeros(num_tests, max(ind_gaps),5);
 dis_mat_currents = zeros(num_tests, max(ind_gaps),5);
 for x = 1: length(cap_test_mat(:,1,1))
     temp = volts(cap_test_mat(x,1,2):cap_test_mat(x,1,3)); 
     [M,I] = max(temp);
     flager1=0;
     t = 0;
     temp_curnt = 1;
     diff_temp = diff(temp);
     while t < (length(temp)- I-1) & (temp_curnt >= 0 |  gradien >= 0  )
         t=t+1;
         gradien= diff_temp(I+t);
         temp_curnt = currents(cap_test_mat(x,1,2)+I+t);
     end
     I = I +t;
         
     temp_new = temp(I:length(temp));
     dis_mat_v(x, 1:length(temp_new),1) = temp_new;
     dis_mat_v(x,1,2) = I ;
     dis_mat_v(x,1,3) = length(temp_new);
     dis_mat_v(x,1,4) = cap_test_mat(x,1,2) + I;
     dis_mat_v(x,1,5) = cap_test_mat(x,1,3);
      
     
     dis_mat_currents(x, 1:(dis_mat_v(x,1,5)-dis_mat_v(x,1,4)+1),1) = currents(dis_mat_v(x,1,4):dis_mat_v(x,1,5));
     dis_mat_currents(x,1,2) =dis_mat_v(x,1,2); % where does discharge start in temp
     dis_mat_currents(x,1,3) = dis_mat_v(x,1,3); % where does it end in temp
     dis_mat_currents(x,1,4) =dis_mat_v(x,1,4);
     dis_mat_currents(x,1,5) = dis_mat_v(x,1,5);
     
 end
 
 % now we have a discharge mat (x,1,3) with the first dimention is the
 % number of cap check cycles x, so dis_mat_currents(x,:,1) is the full
 % current values of the x'th discharge. (same for voltage in the
 % dis_mat_voltage). (x,1,4)is the indeces where discharge beggins in the
 % volts variable. (x,1,5) is where it ends. 
%% sort out 

% At this point we have sorted out the cap checks from the other cycles
% only by current values stored them in cap_test_mat and then created a matrix for the discharges 
% in dis_mat_(cur/volt). However it turns out that a single variable doesnt discriminate  well in
% all cases. So some of our identified cap checks are actually just normal cycles!  We must sort
% them out. We use another important factor for discriminating: length of
% discharge. IF the discharge is longer than a trigger (weighted avg and
% std) then we keep it as a cap test cycle. if not we discard that cycle.
% We go back through the cap_test_mat dis_mat(cur/volt) and get rid of the
% bad cycles

length_dis =zeros(1,length(dis_mat_currents(:,1,1)));
length_char =zeros(1,length(dis_mat_currents(:,1,1)));
  for i = 1: length(dis_mat_currents(:,1,1))
      length_dis(i) = time_v(dis_mat_currents(i,1,5)) - time_v(dis_mat_currents(i,1,4));
      length_char(i)= dis_mat_currents(i,1,2) ;
  end
      
avg_dis_len = mean(length_dis);
find_right_cycles = find((length_dis > ((0.5* avg_dis_len )+ std(length_dis))) & length_char > (0.5*mean(length_char)));
test_cycles = test_cycles(find_right_cycles);
num_cycles =length(find_right_cycles);

find_notcyc = ones(1,length(gaps));
find_notcyc(test_cycles) = 0;
not_test_cycles = find(find_notcyc);
num_notcycles = length(not_test_cycles);

new_captest_mat= cap_test_mat(find_right_cycles,:,:);
new_discharge_c = dis_mat_currents(find_right_cycles,:,:); 
new_discharge_v = dis_mat_v(find_right_cycles,:,:); 
     
dis_mat_currents = new_discharge_c;
cap_test_mat =new_captest_mat;
dis_mat_v =new_discharge_v;
num_tests= length(dis_mat_v(:,1,1));

%% get the not cap checks
% now we store the not cap check cycles or 'normal cycles' into a matrix.
% we will need them later when we again construct discharge and charge
% mats for both voltage and current. 
% we exclud certain bad cycles. These are either fake cycles from a bad
% tester or falsly identified cycles.

 Notcap_test_mat = zeros(length(gaps), max(ind_gaps),3);
     % grab the voltages that are the cap tests
     % create the matrix with the cap tests
    Ncap_counter = 1;
    Notnum_test_count=0;
for j=1: length(ind_gaps) %-1
        Notnum_test_count= Notnum_test_count + 1;
        Notcap_test_mat(Notnum_test_count,1:ind_gaps(j),1)= volts(Ncap_counter: (Ncap_counter + ind_gaps(j)-1))';
        Notcap_test_mat(Notnum_test_count,1, 2) = Ncap_counter;
        Notcap_test_mat(Notnum_test_count,1, 3) = Ncap_counter + ind_gaps(j)-1;
 Ncap_counter = Ncap_counter + ind_gaps(j);  %ticking through the array
end

not_cap_test_mat = Notcap_test_mat(not_test_cycles, :,:);

cur_check = zeros(1, length(not_cap_test_mat(:,1,1)));
count_nzero=0;
for k=1: length(not_cap_test_mat(:,1,1))
     zero_check = currents(not_cap_test_mat(k,1,2):not_cap_test_mat(k,1,3));
     if max(zero_check) >0
         cur_check(k) = 1;
         count_nzero = count_nzero+1;
     end
end

opp_cur_check = find(cur_check ==0);
bad_cycles = not_test_cycles(opp_cur_check);


cur_check = find(cur_check);
TEMP_NCAP = not_cap_test_mat(cur_check, :,:);
not_cap_test_mat = TEMP_NCAP;
not_test_cycles = not_test_cycles(cur_check);

%% trim the not test cycles

% some cycles beggin with a rest (all values =0). We want to cut these
% breaks out.
r= 1;

while r < length(not_cap_test_mat(:,1,1))
    
    temp_trim = currents(not_cap_test_mat(r,1,2):not_cap_test_mat(r,1,3));
    finder_a = find(temp_trim > 0);
    finder_a = min(finder_a);
    
    tmpp_1 = temp_trim(finder_a:end);
    not_cap_test_mat(r, :,1) = 0;
    not_cap_test_mat(r,1:(length(temp_trim)-(finder_a-1)),1) = tmpp_1;
    not_cap_test_mat(r,1,2) = finder_a + not_cap_test_mat(r,1,2);
    r=r+1;
end
 

%% get the not cycles charge 
% in the same way that we did earlier we construct charge mat for the not
% test cycles denoted Nchar_mat(v/currents)
% in the charge cycles we denote Cv portions and CC portions
% not there are some correctional factors as the value1 in our matlab var
% volts is actually value 2 in the original excell file. this causes
% confusion. 

Nchar_mat_v = zeros(length(not_test_cycles), max(ind_gaps),5);
Nchar_mat_currents = zeros(length(not_test_cycles), max(ind_gaps),5);
counter =0;


 for x =1:length(not_cap_test_mat(:,1,1))
    counter = counter +1;
    
    temp = volts(not_cap_test_mat(x,1,2):not_cap_test_mat(x,1,3)); 
     [M,I] = max(temp);
     cc_charI = ceil(I/2);
     I = cc_charI;
     flager1=0;
     t = 1;
     temp_curnt = 1;
     diff_temp = diff(temp);
     while t < (length(temp)- I-1) & (temp_curnt > 0.001) %|  gradien >= 0  ) %while t < (length(temp)- I-1) & (temp_curnt > 0 |  gradien >= 0  )
          t=t+1;
         gradien= diff_temp(I+t);
         temp_curnt = currents(not_cap_test_mat(x,1,2)+I+t);
     end
     I = I +t-1;
     
     cur_tem= currents((not_cap_test_mat(x,1,2)+ 3): (not_cap_test_mat(x,1,2) +I-3));
     vol_tem =volts((not_cap_test_mat(x,1,2)+ 3): (not_cap_test_mat(x,1,2) +I -2));
    % not that there is a +3 that needs to be corrected for between
    % cur_temp and currents same for vol_temp and volts

        % we use medfilt1 and smooth the voltage values then determine when
        % there is a voltage gradient near 0 so that its CV
         vol_tem1 = medfilt1(vol_tem,15);
         vol_temdiff = (diff(vol_tem1));
         minmus = find(vol_temdiff ==0);
 
         cc = min(minmus)+2; % note the +2 correction 
         
         % here we are engineering a soln for a common edge case where
         % there is a slight delay in when the voltage gradient goes to 0.
         if (cur_tem(cc-2) < 0.95* max(cur_tem))
             cc = cc-1;
         end
         
     
     temp_new = temp(1:I);
     Nchar_mat_v(x, 1:length(temp_new),1) = temp_new;
     Nchar_mat_v(x,1,2) = I;
     Nchar_mat_v(x,1,3) = 1;
     if length(cc)>0  
         Nchar_mat_v(x,1,3) = cc ;
     end
     Nchar_mat_v(x,1,4) = not_cap_test_mat(x,1,2);
     Nchar_mat_v(x,1,5) = not_cap_test_mat(x,1,2) +I;
      
     Nchar_mat_currents(x, 1:(Nchar_mat_v(x,1,5)-Nchar_mat_v(x,1,4)+1),1) = currents(Nchar_mat_v(x,1,4):Nchar_mat_v(x,1,5));
     Nchar_mat_currents(x,1,2) =Nchar_mat_v(x,1,2); % where does discharge start in temp
     Nchar_mat_currents(x,1,3) = Nchar_mat_v(x,1,3); % where does it end in temp
     Nchar_mat_currents(x,1,4) =Nchar_mat_v(x,1,4);
     Nchar_mat_currents(x,1,5) = Nchar_mat_v(x,1,5);
     
 end

%% calculate the Notdischarge
% same as the Ncharge but we do not have to identify cv
Ndis_mat_v = zeros(length(not_test_cycles), max(ind_gaps),5);
Ndis_mat_currents = zeros(length(not_test_cycles), max(ind_gaps),5);

 for x = 1: length(not_cap_test_mat(:,1,1))
     temp = volts(not_cap_test_mat(x,1,2):not_cap_test_mat(x,1,3)); 
     [M,I] = max(temp);
     flager1=0;
     t = 0;
     temp_curnt = 1;
     diff_temp = diff(temp);
     
     while t < (length(temp)- I-1) & (temp_curnt >= 0 |  gradien >= 0  )
         t=t+1;
         gradien= diff_temp(I+t);
         temp_curnt = currents(not_cap_test_mat(x,1,2)+I+t);
     end
     I = I +t;

     temp_new = temp(I:length(temp));
     Ndis_mat_v(x, 1:length(temp_new),1) = temp_new;
     Ndis_mat_v(x,1,2) = I ;
     Ndis_mat_v(x,1,3) = length(temp_new);
     Ndis_mat_v(x,1,4) = not_cap_test_mat(x,1,2) + I;
     Ndis_mat_v(x,1,5) = not_cap_test_mat(x,1,3);
      
     
     Ndis_mat_currents(x, 1:(Ndis_mat_v(x,1,5)- Ndis_mat_v(x,1,4)+1),1) = currents(Ndis_mat_v(x,1,4):Ndis_mat_v(x,1,5));
     Ndis_mat_currents(x,1,2) =Ndis_mat_v(x,1,2); % where does discharge start in temp
     Ndis_mat_currents(x,1,3) = Ndis_mat_v(x,1,3); % where does it end in temp
     Ndis_mat_currents(x,1,4) =Ndis_mat_v(x,1,4);
     Ndis_mat_currents(x,1,5) = Ndis_mat_v(x,1,5);
     
 end
 

 
%% calc the charge
% calculate the charge matrix for the  cap check /test cycles
 char_mat_v = zeros(num_tests, max(ind_gaps),5);
 char_mat_currents = zeros(num_tests, max(ind_gaps),5);
 for x = 1: length(cap_test_mat(:,1,1))
    temp = volts(cap_test_mat(x,1,2):cap_test_mat(x,1,3)); 
     [M,I] = max(temp);
     cc_charI = ceil(I/2);
     flager1=0;
     t = 0;
     temp_curnt = 1;
     diff_temp = diff(temp);
     while t < (length(temp)- I-1) & (temp_curnt >= 0 |  gradien >= 0  )
         t=t+1;
         gradien= diff_temp(I+t);
         temp_curnt = currents(cap_test_mat(x,1,2)+I+t);
     end
     I = I +t;
     
     
     cc=cc_charI;
      while cc < (length(temp)- cc_charI-1) & (temp_curnt > 0)
         cc=cc+1;
         gradien= diff_temp(cc);
         temp_curnt = currents(cap_test_mat(x,1,2)+cc);
      end
   
     temp_new = temp(1:I);
     char_mat_v(x, 1:length(temp_new),1) = temp_new;
     char_mat_v(x,1,2) = I;
     char_mat_v(x,1,3) = cc;
     char_mat_v(x,1,4) = cap_test_mat(x,1,2);
     char_mat_v(x,1,5) = cap_test_mat(x,1,2) +I;
      
     char_mat_currents(x, 1:(char_mat_v(x,1,5)-char_mat_v(x,1,4)+1),1) = currents(char_mat_v(x,1,4):char_mat_v(x,1,5));
     char_mat_currents(x,1,2) =char_mat_v(x,1,2); % where does discharge start in temp
     char_mat_currents(x,1,3) = char_mat_v(x,1,3); % where does it end in temp
     char_mat_currents(x,1,4) =char_mat_v(x,1,4);
     char_mat_currents(x,1,5) = char_mat_v(x,1,5);
     
 end
 
 %% plot voltage of discharge
% debugger thats all! generates the voltage a current plots for each cycle
% for dicharge or charge.

%  figure
%      for i = 1:length(cap_test_mat(:,1,1))
%       plt_len = dis_mat_v(i,1,5)- dis_mat_v(i,1,4)  ;
%       plot(time_v(dis_mat_v(i,1,4): dis_mat_v(i,1,5)-1), dis_mat_v(i,1:plt_len,1));
%      figure
%       title('Discharges Voltage curves')
%       xlabel('time (s)')
%       ylabel('voltage (v)')
%       hold on
%      end
%   current curves

%  
 %figure
%       for i = 1: length(dis_mat_currents(:,1,1))
%        plt_len = dis_mat_currents(i,1,5)- dis_mat_currents(i,1,4) ;
%        figure
%        scatter(time_v(dis_mat_currents(i,1,4): dis_mat_currents(i,1,5)-1), dis_mat_currents(i,1:plt_len,1));
%        title('Discharges current curves')
%        xlabel('time (s)')
%        ylabel('amp (A)')
%        hold on
%       end
%       
%       
%   %% plot charge
%   
%      for i = 1:length(cap_test_mat(:,1,1))
%       plt_len = Nchar_mat_v(i,1,3);
%       plt_len2 = (not_cap_test_mat(i,1,3) - not_cap_test_mat(i,1,2))+1;
%       figure
%       plot(time_v(Nchar_mat_v(i,1,4): (Nchar_mat_v(i,1,4)+ Nchar_mat_v(i,1,3)-1)), Nchar_mat_v(i,1:plt_len,1));
%       title('not cap Charges Voltage cc curves')
%       figure
%       plot(time_v(not_cap_test_mat(i,1,2):not_cap_test_mat(i,1,3)), not_cap_test_mat(i,1:plt_len2,1));
%       hold on
%       plot(time_v(not_cap_test_mat(i,1,2):not_cap_test_mat(i,1,3)), currents(not_cap_test_mat(i,1,2):not_cap_test_mat(i,1,3)));
%       title('not cap full curves')
%       xlabel('time (s)')
%       ylabel('voltage (v)')    
%      end
% % %      
     
%      %  current curves
% 
% %  



% 
%    for i = 1:length(cap_test_mat(:,1,1))
%       plt_len = char_mat_v(i,1,5)- char_mat_v(i,1,4)  ;
%       plot(time_v(char_mat_v(i,1,4): char_mat_v(i,1,5)-15), char_mat_v(i,1:plt_len-14,1));
%      figure
%       title('Charges Voltage curves')
%       xlabel('time (s)')
%       ylabel('voltage (v)')
%       hold on
%      end
%  



 %figure
%       for i = 1: length(cap_test_mat(:,1,1))
%        plt_len = char_mat_currents(i,1,5)- char_mat_currents(i,1,4) ;
%        figure
%        scatter(time_v(char_mat_currents(i,1,4): char_mat_currents(i,1,5)-1), char_mat_currents(i,1:plt_len,1));
%        title('Charge current curves')
%        xlabel('time (s)')
%        ylabel('amp (A)')
%        hold on
%       end
   %% Compute Discharge Capacity
   % Here we put everything togeather and get the discharge and charge
   % capacity we also do the cc times
   dis_cap = zeros(num_cycles,1);
   time_d = zeros(1,length(dis_mat_currents(:,1,1)));
   
   Ntime_d = zeros(1,length(Ndis_mat_currents(:,1,1)));
   Ntime_c= zeros(1,length(Nchar_mat_currents(:,1,1)));
   Ntime_cv_char = zeros(1,length(dis_mat_currents(:,1,1)));
   
   
   for i = 1: length(Ndis_mat_currents(:,1,1))
       time_tmp = time_v(Ndis_mat_currents(i,1,4): (Ndis_mat_currents(i,1,5)));
       length_dis_tmp= Ndis_mat_currents(i,1,5)- Ndis_mat_currents(i,1,4)+1;
       Ntime_d(i) = time_v(Ndis_mat_currents(i,1,5)) - time_v(Ndis_mat_currents(i,1,4));
       Ntime_c(i) = time_v(Nchar_mat_currents(i,1,5)) - time_v(Nchar_mat_currents(i,1,4));
       Ntime_cv_char(i) = time_v(Nchar_mat_currents(i,1,5)) - time_v(Nchar_mat_currents(i,1,4)+ Nchar_mat_currents(i,1,3));    
   end
   % above we calc the  cv charge time and the cc time is computed outside
   % the function 
  
   % below we do a numerical integration to get the discharge capacity
   
   for i = 1: length(dis_mat_currents(:,1,1))
       time_tmp = time_v(dis_mat_currents(i,1,4): (dis_mat_currents(i,1,5)));
       length_dis_tmp= dis_mat_currents(i,1,5)-dis_mat_currents(i,1,4)+1;
       dis_cap(i) = trapz(time_tmp, dis_mat_currents(i,1:length_dis_tmp,1));
       time_d(i) = time_v(dis_mat_currents(i,1,5)) - time_v(dis_mat_currents(i,1,4));
   end
  
   dis_cap= -dis_cap;
   dis_cap= dis_cap/3600;
   debugg =dis_cap;
   
   
   % now we calc the charge capacity in a simular way.
   char_cap = zeros(num_cycles,1);
   time_c = zeros(1,length(dis_mat_currents(:,1,1)));
   time_cv_char=zeros(1,length(dis_mat_currents(:,1,1)));
   for i = 1: length(char_mat_currents(:,1,1))
       time_sc = time_v(char_mat_currents(i,1,4): (char_mat_currents(i,1,5)));
       length_dis_tmp= char_mat_currents(i,1,5)-char_mat_currents(i,1,4)+1;
       char_cap(i) = trapz(time_sc, char_mat_currents(i,1:length_dis_tmp,1));
       time_c(i) = time_v(char_mat_currents(i,1,5)) - time_v(char_mat_currents(i,1,4));
       time_cv_char(i) = time_v(char_mat_currents(i,1,5)) - time_v(char_mat_currents(i,1,4)+char_mat_currents(i,1,3));
    
    end
   
   char_cap= char_cap/3600;
   
   figure
   scatter(test_cycles,char_cap)
   xlabel('test cycles')
   ylabel('charge capacity')
   title('Charge Capacity')
   
   figure
   scatter(test_cycles, dis_cap)
   xlabel('test cycles')
   ylabel('charge capacity')
    title('Discharge Capacity')
   
   
     
   %% Gradient
   
   % unfinished work on voltage gradients near transitions.
   drv_tran = zeros(length(Ndis_mat_currents(:,1,1)), 4);
   
   
   for i = 1:length(not_cap_test_mat(:,1,1))
       tmp1 =  volts(Nchar_mat_currents(i,1,4):(Ndis_mat_currents(i,1,4)+9));
       tmp1_t = time_v(Nchar_mat_currents(i,1,4):(Ndis_mat_currents(i,1,4)+9));
       tmp1_dvdt = gradient(tmp1,tmp1_t);
       [M,I] = max(abs(tmp1_dvdt));
       drv_tran(i,1) = tmp1_dvdt(I);
       
       tmp2 =  volts(Nchar_mat_currents(i,1,5):(Ndis_mat_currents(i,1,5)+1));
       tmp2_t= time_v(Nchar_mat_currents(i,1,5):(Ndis_mat_currents(i,1,5)+1));
       tmp2_dvdt = gradient(tmp2,tmp2_t);
       [M,I] = max(abs(tmp2_dvdt)); %minnotabs
       drv_tran(i,2) = tmp2_dvdt(I);
        
       tmp3 =  volts(Ndis_mat_currents(i,1,4):(Ndis_mat_currents(i,1,4)+2));
       tmp3_t = time_v(Ndis_mat_currents(i,1,4):(Ndis_mat_currents(i,1,4)+2));
       tmp3_dvdt = gradient(tmp3,tmp3_t);
       [M,I] = max(abs(tmp3_dvdt)); %min notabs
       drv_tran(i,3) = tmp3_dvdt(I);
       
       if  i < (length(not_cap_test_mat(:,1,1))-1)
       tmp4 =  volts((Ndis_mat_currents(i,1,5)):(Ndis_mat_currents(i,1,5)+2));
       tmp4_t = time_v((Ndis_mat_currents(i,1,5)):(Ndis_mat_currents(i,1,5)+2));
       tmp4_dvdt = gradient(tmp4,tmp4_t);
       [M,I] = max(abs(tmp4_dvdt));
       drv_tran(i,4) = tmp4_dvdt(I);
       end
   end
       
   
% 
%    figure
%    scatter(test_cycles, dis_cap)
%    title('Charge capacity')
%    xlabel('Number of Capacitance tests')
%    ylabel('Amp Hours')

%    
%    figure
%    scatter(test_cycles, char_cap)
%    title('disCharge capacity')
%    xlabel('Number of Capacitance tests')
%    ylabel('Amp Hours')
%    
   
%    figure
%    histogram(gaps)
%    title('Distribution: Time length of cycle (SNL 1C)')
%    xlabel('Time(s)')
%    ylabel('Frequncy')
  
%  figure
%    histogram(time_c)
%    title('The Charge cc+cv time distribution')
%    xlabel('Time (s)')
%    
%  figure
%     histogram(time_cc_char)
%    title('The Charge cc time distribution')
%    xlabel('Time (s)')
   
%    for i = 1: length(char_mat_currents(:,1,1))
%        figure
%        time_cc= time_v(char_mat_currents(i,1,4): ((char_mat_currents(i,1,4)+(char_mat_currents(i,1,3)))));
%        volts_cc= volts(char_mat_currents(i,1,4): ((char_mat_currents(i,1,4)+(char_mat_currents(i,1,3)))));
%        scatter(time_cc,volts_cc); 
%    end

if length(drv_tran) ==0
    drv_tran = 1;
end

if length(not_test_cycles) ==0
   not_test_cycles = 1;
end

%% really important final correction for the oxford set.
% representation of cycles is only the cycles and no other ones so we need
% to include a correction

if length(Ntime_d) ==0 & length(Ntime_c) ==0 
    Ntime_d = 1;
    Ntime_c =1;
    Ntime_cv_char = 1;
    test_cycles= test_cycles*100;
end

%end

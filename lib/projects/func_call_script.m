import_data = readmatrix('SNL_18650_NMC_25C_0-100_0.5-1C_a_timeseries.csv');
[drv_tran1a, Ntest_cycles1a, Stest_cycles1a, Sdisch_cap1a, Schar_cap1a,time1a_d, time1a_c, time1a_cv] = get_the_values_var(import_data);
import_data = readmatrix('SNL_18650_NMC_25C_0-100_0.5-1C_b_timeseries.csv');
[drv_tran1b, Ntest_cycles1b, Stest_cycles1b, Sdisch_cap1b, Schar_cap1b,time1b_d, time1b_c,time1b_cv] = get_the_values_var(import_data);
import_data = readmatrix('SNL_18650_NMC_25C_0-100_0.5-1C_c_timeseries.csv');
[drv_tran1c, Ntest_cycles1c, Stest_cycles1c, Sdisch_cap1c, Schar_cap1c,time1c_d, time1c_c,time1c_cv] = get_the_values_var(import_data);
import_data = readmatrix('SNL_18650_NMC_25C_0-100_0.5-1C_d_timeseries.csv');
[drv_tran1d, Ntest_cycles1d,Stest_cycles1d, Sdisch_cap1d, Schar_cap1d,time1d_d, time1d_c,time1d_cv] = get_the_values_var(import_data);
import_data = readmatrix('SNL_18650_NMC_25C_0-100_0.5-2C_a_timeseries.csv');
[drv_tran2a, Ntest_cycles2a,Stest_cycles2a, Sdisch_cap2a, Schar_cap2a,time2a_d, time2a_c,time2a_cv] = get_the_values_var(import_data);
import_data = readmatrix('SNL_18650_NMC_25C_0-100_0.5-2C_b_timeseries.csv');
[drv_tran2b, Ntest_cycles2b,Stest_cycles2b, Sdisch_cap2b, Schar_cap2b,time2b_d, time2b_c,time2b_cv] = get_the_values_var(import_data);
import_data = readmatrix('SNL_18650_NMC_25C_0-100_0.5-3C_a_timeseries.csv');
[drv_tran3a, Ntest_cycles3a,Stest_cycles3a, Sdisch_cap3a, Schar_cap3a,time3a_d, time3a_c,time3a_cv] = get_the_values_var(import_data);
import_data = readmatrix('SNL_18650_NMC_25C_0-100_0.5-3C_b_timeseries.csv');
[drv_tran3b, Ntest_cycles3b,Stest_cycles3b, Sdisch_cap3b, Schar_cap3b,time3b_d, time3b_c,time3b_cv] = get_the_values_var(import_data);
import_data = readmatrix('SNL_18650_NMC_25C_0-100_0.5-3C_c_timeseries.csv');
[drv_tran3c, Ntest_cycles3c,Stest_cycles3c, Sdisch_cap3c, Schar_cap3c,time3c_d, time3c_c,time3c_cv] = get_the_values_var(import_data);
import_data = readmatrix('SNL_18650_NMC_25C_0-100_0.5-3C_d_timeseries.csv');
[drv_tran3d, Ntest_cycles3d,Stest_cycles3d, Sdisch_cap3d, Schar_cap3d,time3d_d, time3d_c,time3d_cv] = get_the_values_var(import_data);
import_data = readmatrix('HNEI_18650_NMC_LCO_25C_0-100_0.5-1.5C_a_timeseries.csv');
[drv_tranHa, Ntest_cyclesHa,Stest_cyclesHa, Sdisch_capHa, Schar_capHa,timeHa_d, HtimeHa_c,HtimeHa_cv] = get_the_values_var(import_data);
import_data = readmatrix('OX_1-1_pouch_LCO_40C_0-100_2-1.84C_a_timeseries.csv');
[drv_tranOa, Ntest_cyclesOa,Stest_cyclesOa, Sdisch_capOa, Schar_capOa,timeOa_d, HtimeOa_c,HtimeOa_cv] = get_the_values_var(import_data);



%import_data = readmatrix(''HNEI_18650_NMC_LCO_25C_0-100_0.5-1.5C_b_timeseries.csv');
 %[drv_tranH, Ntest_cyclesH,Stest_cyclesH, Sdisch_capH, Schar_capH,time3H, Htime3d_c,Htime3d_cv] = get_the_values_var(import_data);

time1a_cc = time1a_c - time1a_cv;
time1b_cc = time1b_c - time1b_cv;
time1c_cc = time1c_c - time1c_cv;
time1d_cc = time1d_c - time1d_cv;

time2a_cc = time2a_c - time2a_cv;
time2b_cc = time2b_c - time2b_cv;

time3a_cc = time3a_c - time3a_cv;
time3b_cc = time3b_c - time3b_cv;
time3c_cc = time3c_c - time3c_cv;
time3d_cc = time3d_c - time3d_cv;
timeHa_cc = HtimeHa_c - HtimeHa_cv;
%timeOa_cc = HtimeOa_c - HtimeOa_cv;

figure
   scatter(Stest_cycles1a, Schar_cap1a, 's')
   hold on
   scatter(Stest_cycles1b, Schar_cap1b, 's')
   hold on
   scatter(Stest_cycles1c, Schar_cap1c, 's')
   hold on
   scatter(Stest_cycles1d, Schar_cap1d, 's')
   hold on
   scatter(Stest_cycles2a, Schar_cap2a, 'd')
   hold on
   scatter(Stest_cycles2b, Schar_cap2b, 'd')
   hold on
   scatter(Stest_cycles3a, Schar_cap3a, 'x')
   hold on
   scatter(Stest_cycles3b, Schar_cap3b, 'x')
   hold on
   scatter(Stest_cycles3c, Schar_cap3c, 'x')
   hold on
   scatter(Stest_cycles3d, Schar_cap3d, 'x')

%  
   legend('SNL 1a','SNL 1b','SNL 1c','SNL 1d','SNL 2a','SNL 2b','SNL 3a','SNL 3b','SNL 3c','SNL 3d');
   title('Charge capacity')
   xlabel('Number of Capacitance tests')
   ylabel('Amp Hours')
   
figure
   scatter(Stest_cycles1a, Sdisch_cap1a, 's')
   hold on
   scatter(Stest_cyclesHa, Sdisch_capHa, '.')
   hold on
   scatter(Stest_cyclesOa(1:29), Sdisch_capOa(1:29), 'x')
%    
%    
   
   legend('SNL 1a','HNEI a','Oxford a');
   title('Discharge capacity')
   xlabel('Number of Capacitance tests')
   ylabel('Amp Hours')
   
%    discharge_times= cat(2, time1a_d, time1b_d,time1c_d,time1d_d, time2a_d, time2b_d,time3a_d,time3b_d,time3c_d,time3d_d);
%    charge_times= cat(2, time1a_c, time1b_c,time1c_c,time1d_c, time2a_c, time2b_c,time3a_c,time3b_c,time3c_c,time3d_c);
%    char_cc = cat(2,time1a_cc,time1b_cc,time1c_cc,time1d_cc,time2a_cc,time2b_cc,time3a_cc,time3b_cc,time3c_cc,time3d_cc);
%    char_cv = charge_times- char_cc;
%    

figure
   scatter(Ntest_cycles1a, time1a_d, 's')
   hold on
   scatter(Ntest_cycles1b, time1b_d, 's')
   hold on
   scatter(Ntest_cycles1c, time1c_d, 's')
   hold on
   scatter(Ntest_cycles1d, time1d_d, 's')
   hold on
   scatter(Ntest_cycles2a, time2a_d, 'd')
   hold on
   scatter(Ntest_cycles2b,time2b_d, 'd')
   hold on
   scatter(Ntest_cycles3a, time3a_d, 'x')
   hold on
   scatter(Ntest_cycles3b,time3b_d, 'x')
   hold on
   scatter(Ntest_cycles3c, time3c_d, 'x')
   hold on
   scatter(Ntest_cycles3d, time3d_d, 'x')
   hold on
 
   legend('SNL 1a','SNL 1b','SNL 1c','SNL 1d','SNL 2a','SNL 2b','SNL 3a','SNL 3b','SNL 3c','SNL 3d');
   title('The discharge time SNL')
   xlabel('Cycle number')
   ylabel('Time (s)')
   
   figure
   scatter(Ntest_cycles1a, time1a_c, 's')
   hold on
   scatter(Ntest_cycles1b, time1b_c, 's')
   hold on
   scatter(Ntest_cycles1c, time1c_c, 's')
   hold on
   scatter(Ntest_cycles1d, time1d_c, 's')
   hold on
   scatter(Ntest_cycles2a, time2a_c, 'd')
   hold on
   scatter(Ntest_cycles2b,time2b_c, 'd')
   hold on
   scatter(Ntest_cycles3a, time3a_c, 'x')
   hold on
   scatter(Ntest_cycles3b,time3b_c, 'x')
   hold on
   scatter(Ntest_cycles3c, time3c_c, 'x')
   hold on
   scatter(Ntest_cycles3d, time3d_c, 'x')
   hold on
 
   legend('SNL 1a','SNL 1b','SNL 1c','SNL 1d','SNL 2a','SNL 2b','SNL 3a','SNL 3b','SNL 3c','SNL 3d');
   title('The Charge time SNL')
   xlabel('Cycle number')
   ylabel('Time (s)')
   
  figure
   scatter(Ntest_cycles1a, time1a_cv, 's')
   hold on
   scatter(Ntest_cycles1b, time1b_cv, 's')
   hold on
   scatter(Ntest_cycles1c, time1c_cv, 's')
   hold on
   scatter(Ntest_cycles1d, time1d_cv, 's')
   hold on
   scatter(Ntest_cycles2a, time2a_cv, 'd')
   hold on
   scatter(Ntest_cycles2b,time2b_cv, 'd')
   hold on
   scatter(Ntest_cycles3a, time3a_cv, 'x')
   hold on
   scatter(Ntest_cycles3b,time3b_cv, 'x')
   hold on
   scatter(Ntest_cycles3c, time3c_cv, 'x')
   hold on
   scatter(Ntest_cycles3d, time3d_cv, 'x')
   hold on
 
   legend('SNL 1a','SNL 1b','SNL 1c','SNL 1d','SNL 2a','SNL 2b','SNL 3a','SNL 3b','SNL 3c','SNL 3d');
   title('The Charge only CV time SNL')
   xlabel('Cycle number')
   ylabel('Time (s)')
   
   figure
   scatter(Ntest_cycles1a, time1a_cc, 's')
   hold on
   scatter(Ntest_cycles1b, time1b_cc, 's')
   hold on
   scatter(Ntest_cycles1c, time1c_cc, 's')
   hold on
   scatter(Ntest_cycles1d, time1d_cc, 's')
   hold on
   scatter(Ntest_cycles2a, time2a_cc, 'd')
   hold on
   scatter(Ntest_cycles2b,time2b_cc, 'd')
   hold on
   scatter(Ntest_cycles3a, time3a_cc, 'x')
   hold on
   scatter(Ntest_cycles3b,time3b_cc, 'x')
   hold on
   scatter(Ntest_cycles3c, time3c_cc, 'x')
   hold on
   scatter(Ntest_cycles3d, time3d_cc, 'x')
   hold on
 
   legend('SNL 1a','SNL 1b','SNL 1c','SNL 1d','SNL 2a','SNL 2b','SNL 3a','SNL 3b','SNL 3c','SNL 3d');
   title('The Charge only CC time SNL')
   xlabel('Cycle number')
   ylabel('Time (s)')
   
%    
%    figure
%    scatter( Ntest_cycles1a,drv_tran1a(:,1))
%    title('Initial Charge Voltage Gradient')
%    xlabel('Cycle number')
%    ylabel('dv/dt')
%    figure
%    %hold on
%    scatter( Ntest_cycles1b,drv_tran1b(:,1))
%    %hold on
%    figure
%    scatter( Ntest_cycles1c,drv_tran1c(:,1))
%    figure
%    %hold on
%    scatter( Ntest_cycles1d,drv_tran1d(:,1))
%    figure
%    %hold on
%    scatter( Ntest_cycles2a,drv_tran2a(:,1))
%    %hold on
%    figure
%    scatter( Ntest_cycles2b,drv_tran2b(:,1))
%    figure
%    %hold on
%    scatter( Ntest_cycles3a,drv_tran3a(:,1))
%    %hold on
%    figure
%    scatter( Ntest_cycles3b,drv_tran3b(:,1))
%    %hold on
%    figure
%    scatter( Ntest_cycles3c,drv_tran3c(:,1))
%    %hold on
%    figure
%    scatter( Ntest_cycles3d,drv_tran3d(:,1))
%    
%    legend('SNL 1a','SNL 1b','SNL 1c','SNL 1d','SNL 2a','SNL 2b','SNL 3a','SNL 3b','SNL 3c','SNL 3d');
%    title('Voltage gradient at begging of Charge')
%    xlabel('Cycle number')
%    ylabel('Time (s)')
   
   
   
   
   
%    figure
%    scatter( Ntest_cycles1a,drv_tran1a(:,2))
%    figure
%    scatter( Ntest_cycles1a,drv_tran1a(:,3))
%    figure
%    scatter( Ntest_cycles1a,drv_tran1a(:,4))
%    
%    
%    
%    figure
%    histogram(charge_times)
%    title('The Charge time cc + cv distribution')
%    xlabel('Time (s)')
%    
%    figure
%    histogram(char_cc)
%    title('The Charge time cc only distribution')
%    xlabel('Time (s)')
%    
%    figure
%    histogram(char_cv)
%    title('The Charge time cv only distribution')
%    xlabel('Time (s)')
%    
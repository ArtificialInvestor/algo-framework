###########################################################
# ALGORITHM FRAMEWORK V1.2 - 08/09/15 - Marcus Williamson #
###########################################################
# PLEASE SEE EVERNOTE PSEUDOCODE FOR MORE DETAILS ON CODE #
###########################################################

'''
MISSING:
- Risk management example logic
- Abilty to pickup existing open positions on algorithm restart
'''

#import libraries
import math
import pandas
import datetime
import pytz
import numpy as np
import pandas as pd
import statsmodels.api as sm


################################# [1] INITIALIZATION #####################################

'''
This is called when algorithm is first switched on defines fixed aspects in algos operation placeholder security sometimes defined before future csv import can import csv list of securities here but is ONE OFF operation
'''
def initialize(context):
    
    #define commission
    set_commission(commission.PerShare(cost=1.00))
    set_commission(commission.PerTrade(cost=1.00))
    set_slippage(slippage.FixedSlippage(spread=0.013))
    set_symbol_lookup_date('2014-01-01')
    
    #set_benchmark(symbol('QAI')) #multi strategy hedgefund tracker CORRECT BENCHMARK COMPARISON

       
    context.securities = [sid(8554),sid(19920),sid(4283), etc...] #define universe
    
    #STRATEGY 1 DEFINED SECURITIES AND INPUTS
    inputs1 = sid(8554)
    lookback1 = x
    param1 = x
    
    #STRATEGY 2 DEFINED SECURITIES AND INPUTS
    inputs2 = sid(19920)
    lookback2 = x
    param2 = x

    ...
    
    #STRATEGY N DEFINED SECURITIES AND INPUTS
    inputsN = [sid(4283)]
    lookbackN = x
    paramN = x
    
    #INITIALIZATION OF MODULES ON FIRST RUN
    try: 
        context.first_time #if this is the first time will error onto except
        
    except:
        context.first_time = False #no longer first time 
        
        #DEFINING KEY VARIABLES
        thres_rebal = 0.1 #defining a target vs existing position difference threshold
        
        w1 = 0.33 #portfolio allocations for each alpha generator
        w2 = 0.33
        ...
        wN = 0.33
        
        #DEFINING PORTFOLIO MANAGER
        context.p_manager = PortfolioManagerWeighted(thres = thres_rebal)
        
        #DEFINING EXECUTION HANDLER
        context.exec_handler = ExecutionHandlerMarket()
        
        #DEFINING RISK MANAGER
        context.r_manager = RiskManagerPortfolio()
        
        #DEFINING ALPHAGENERATORS
        context.alpha_1 = AlphaGeneratorStrat1(inputs1, lookback1, param1)
        context.alpha_2 = AlphaGeneratorStrat2(inputs2, lookback2, param2)
        ...
        context.alpha_N = AlphaGeneratorStrat3(inputsN, lookbackN, paramN)
        
        #ADDING ALPHAGENERATORS TO PORTFOLIO MANAGER
        context.p_manager.add_alpha_generator(context.alpha_1, w1)
        context.p_manager.add_alpha_generator(context.alpha_2, w2)
        ...
        context.p_manager.add_alpha_generator(context.alpha_N, wN)


################################### [2] SCHEDULING ########################################

    '''
    THIS SECTION IS STILL PART OF INITIALIZE: All main operations of the algorithm that occur during the market opening times are triggered with time based rules instead of manual comparisons taking place every minute bar, they are roughly broken down into housekeeping and strategies, housekeeping ensures records are kept of portfolio metrics and orders are occuring correctly. Strategy timings are based on the requirements of the particular algorithm. Strategies that are run every minute bar are barking up the wrong tree, however they can be placed in handle data...
    '''
    #HOUSEKEEPING  
    schedule_function(record_daily_values ,date_rules.every_day(),
                      time_rules.market_close(hours=0,minutes=5),half_days=True)
    schedule_function(check_orders ,date_rules.every_day(),
                      time_rules.market_close(hours=0,minutes=5),half_days=True)

    
    #STRATEGY TIMINGS
    #to run very day 30 mins into market open
    schedule_function(alpha_strat1 ,date_rules.every_day(),time_rules.market_open(hours=0,minutes=30),half_days=True)
    ...
    
    for minute in range(5,385,1): #to run every minute 5mins after open
        schedule_function(alpha_strat2 ,time_rule=time_rules.market_open(minutes=minute),half_days=True)
        schedule_function(alpha_stratN ,time_rule=time_rules.market_open(minutes=minute),half_days=True)
        ...
    

    # END INITIALIZE 
    
################################# [3] BEFORE OPEN #########################################

'''
Anything in here will be executed the night before the market opens, this is some time in the early hours of the morning, importing of CSV's normally happens here, also if using dynamic signals this is where they are introduced for rest of the algorithm during the trading day
'''
def before_trading_start(context, data):
    
    pass

################################ [4] STRATEGY HANDLER #####################################

'''
This section contains the strategy functions which are run during market open hours on triggering by a scheduled function. The strategies are activated at specific times during the day this section is stackable
'''
#STRATEGY 1 EVENT 
def alpha_strat1(context, data):
    
    #LOGIC GOES HERE!
        context.p_manager.alpha_rebalance[context.alpha_1] = True #flag to be rebalanced
    
        activate_compute_target(context, data) #trigger computing of new targets

#STRATEGY 2 EVENT 
def alpha_strat2(context, data):
    
    #LOGIC GOES HERE!
        context.p_manager.alpha_rebalance[context.alpha_2] = True #flag to be rebalanced
    
        activate_compute_target(context, data) #trigger computing of new targets

        
#STRATEGY N EVENT 
def alpha_stratN(context, data):
    
    #LOGIC GOES HERE!
        context.p_manager.alpha_rebalance[context.alpha_N] = True #flag to be rebalanced
    
        activate_compute_target(context, data) #trigger computing of new targets
    

################################# [5] EVENT HANDLER ###################################### 

'''
This is where it all comes together, when the scheduled function has run for the specific alpha strategy it will call this function to compute target. This calls the portfolio manager to promp the alpha generator for what it wants allocated to its strategy then this is tied together into a target portfolio and sent to the risk manager who then examines and modifies sizing if necessary, then passes it onto the market execution handler to action order
'''
#ORDER PROCESSING
def activate_compute_target(context, data):
    
    context.p_manager.compute_target(context, data) #compute new target port in port manager
    
    pretarget = context.p_manager.target_portfolio #initial target portfolio is generated
    
    context.r_manager.compute_risk(context, data, pretarget) #examining risk of target port
    
    target = context.r_manager.risked_target_portfolio #returned risk adjusted target port
    
    context.exec_handler.compute_orders(context, data, target) #send target to execution man

    
'''
The handle data function is called every bar of data      
'''
def handle_data(context, data):
    #if strategy requires to run on every bar of data it can be placed within here or called
    pass
    
    
#RECORDING DAILY METRICS    
def record_daily_values(context, data):
    
    #keeping track of leverage postions and any other data that is relevant to daily operation
    record(leverage = context.account.leverage)
    record(market_exposure = context.account.net_leverage)

    longs = shorts = 0
    for position in context.portfolio.positions.itervalues():
        if position.amount > 0:
            longs += 1
        if position.amount < 0:
            shorts += 1
            
    record(long_count=longs, short_count=shorts)#, zscore = context.zscr)  

'''
This function is called at the end of the trading day and needs to compare the target portfolio that was executed against the actual open orders and any that have failed. If there is a mismatch then a contingency needs to be planned, calling the relevant pair arm to close or to trigger a full portfolio rebalance in order to shore up positions. Closing incorrect positions is top priority as uncalculated exposure could lead to nasty concequences
'''
#CHECKING ORDERS    
def check_orders(context,data):
    
    #Check that actual positions match what is expected by portfolio manager
    #check that portfolio.positions matches target_portfolio!!
    
    #CLOSING FAILED MARKET ORDERS
    D = get_open_orders() 
    for L in D: 
        for ID in D[L]:
            cancel_order(ID) # cancel order
            log.info("Closing unfilled order: {0}".format(ID))
      
    
################################ [6] CLASSES TO IMPLEMENT #################################

'''
These classes to implement represent classes that later aspects of the code call when different strategies require the usage of them. They provide structure and a framework for iterative usage. AlphaGenerator 'abstract class' keeps track of positions and allocations requested, it serves as the class from which the individual alpha generators inherit python dictionaries and functions, so that they can be called in an iterative way later in the program. In other words it provides backbone structure to function which later takes varying inputs
'''
#ALPHA GENERATOR CLASS
class AlphaGenerator(object):

    def __init__(self):
        
        self.alloc = dict() # allocation wanted
                
    def compute_allocation(self, context, data):
        
        raise NotImplementedError() #if there is attempt to override this method then error    
   

'''
Portfolio manager module manages the portfolio on the chosen frequency of strategy. It has alpha generators under control that get edge and ask for allocation. It then compute a target allocation being helped by a risk manager before sending to execution handler
'''
#PORTFOLIO MANAGER
class PortfolioManager(object):

    def __init__(self):
        
        self.target_portfolio = dict() #target_portfolio
        
        self.list_alpha = [] #list of strategies
        
        self.alpha_rebalance = dict() #keep track if we want to get new signals from alpha generators
        
    
    def add_alpha_generator(self, alpha_generator): #add a new alpha generator to portfolio
        
        self.list_alpha.append(alpha_generator) #append it to list
        
        self.alpha_rebalance[alpha_generator] = False #rebalanced flag set 

    
    def compute_target(self, context, data): #computes the target portfolio
        
        raise NotImplementedError() 


################################## [7] ALPHA STRATEGIES ##################################

'''
All alpha generators go here, this can be singular or as many as is desired, an alpha generator can also be used to decide portfolio allocations of the other strategies by consulting self.list_alpha.append and then adjusting the associated weights. This for example could be modfying trend following bias to mean reversion bias in portfolio weighting. This is stackable!!
'''
#ALPHA GENERATOR STRATEGY 1 CLASS #########################
class AlphaGeneratorStrat1(AlphaGenerator): # MEAN REVERSION
    
    def __init__(self, input1, lookback1, param1): #define
        
        AlphaGenerator.__init__(self) #utilising abstract alphagenerator class definitions 
        #DEFINING TOP LEVEL VARIABLES OFF OF INPUT 
        self.input1 = input1    
        self.lookback1 = lookback1 
        self.param1 = param1
        
    #CUSTOM FUNCTIONS #############       
    def update_parameters(self, lookback1, data):  
        
        self.average = data[self.input1].mavg(self.lookback1)
        self.stdev = data[self.input1].stddev(self.lookback1)
        etc...
            
    #COMPUTE ALLOCATIONS DESIRED
    def compute_allocation(self, context, data):
        
        #CALLING EXAMPLE FUNCTION
        if get_datetime().hour == 14 and get_datetime().minute == 35: #do this once per day
            self.update_parameters(self.lookback1, data) #get latest mavg and stdev
        
        
        #INSERT TRADING LOGIC HERE WHICH YIELDS ALLOC
        if z < y:
            self.alloc[self.input1] = x
        else:
            pass
        
                    
             
#ALPHA GENERATOR STRATEGY 2 CLASS #########################
class AlphaGeneratorStrat2(AlphaGenerator): # 
    
    def __init__(self, input2, lookback2, param2):
        
        AlphaGenerator.__init__(self) #utilising class
        
        self.input2 = input2   
        self.lookback2 = lookback2
        self.param2 = param2
        
    #COMPUTING ALLOCATION DESIRED
    def compute_allocation(self, context, data):
        
        #INSERT TRADING LOGIC HERE WHICH YIELDS ALLOC
        if z < y:
            self.alloc[self.input2] = x
        else:
            pass
        

###########################################################


... TRADING STRATEGIES ...

        
#ALPHA GENERATOR STRATEGY N CLASS #########################
class AlphaGeneratorStratN(AlphaGenerator):
    
    def __init__(self, inputN, lookbackN, paramN): #define
        
        AlphaGenerator.__init__(self) #utilising abstract alphagenerator class definitions 
        
        #DEFINING TOP LEVEL VARIABLES OFF OF INPUT 
        self.inputN = inputN 
        self.lookbackN = lookbackN
        self.paramN = paramN
        
    #CUSTOM FUNCTIONS #############       
    def update_spreads(self, lookback, data):  
        
        #custom logic goes here
        pass
    
    
    #COMPUTE ALLOCATIONS DESIRED
    def compute_allocation(self, context, data):
                   
        self.update_spreads(self.lookback, data) #get latest mavg and stdev
        
        #custom trading logic
        
        self.alloc[self.inputN] = x    
    
    
################################### [8] PORTFOLIO MANAGER #################################

'''
Heart and soul of algorithm, everything passes through the portfolio manager in some form, alpha generators are added into the portfolio and it manages the allocations requested from each alpha generator it computes targets portfolios which are passed to risk manager to evaluate before they are sent to execution handler
'''
#PORTFOLIO MANAGER CLASS
class PortfolioManagerWeighted(PortfolioManager):

    def __init__(self, thres):
        
        PortfolioManager.__init__(self) #utilising abstract port manager class definitions 
        
        self.list_weight_alpha = dict() #defining
        
        self.thres = thres #reassigning threshold from initialise
        
        
    #ADD ALPHA GENERATORS
    def add_alpha_generator(self, alpha_generator, weight): 
        #add new alpha generator to port
        
        self.list_alpha.append(alpha_generator) #append
        
        self.list_weight_alpha[alpha_generator] = weight #give it input weighting
        
        self.alpha_rebalance[alpha_generator]   = False #set rebalance flag false

        
    #COMPUTE TARGETS 
    def compute_target(self, context, data):

        self.get_new_alpha_allocation(context, data) #refresh allocation asked by alpha gens

        self.target_portfolio = dict() #clear target portfolio allocations ready

        for alpha in self.list_alpha: #for each alpha add allocation to the target

            for stock in alpha.alloc:

                alloc_alpha = alpha.alloc[stock] * self.list_weight_alpha[alpha] 
                #adjust stock allocation by strategy allocation so rule is not compromised

                self.target_portfolio[stock] = alloc_alpha 
                #add target allocation to target portfolio
                
                
            alpha.alloc = dict() #reset dictionary to get rid of old entries now in target portfolio
        
        port_value = context.portfolio.portfolio_value #geting portfolio value
        
        for stock in context.portfolio.positions:
            
            if stock in self.target_portfolio: #check if its in target portfolio first
            
                amount = context.portfolio.positions[stock].amount
            
                price  = data[stock].price
            
                alloc_stock = amount * price / port_value #getting current allocation of stock
            
                if abs(self.target_portfolio[stock] - alloc_stock) < self.thres: #if close enough
                
                    self.target_portfolio[stock] = alloc_stock #no need to change
                else:
                    pass
                
    #REFRESH ALPHA ALLOCATIONS
    def get_new_alpha_allocation(self, context, data):
        
        for alpha in self.list_alpha:
            
            if self.alpha_rebalance[alpha]:
                
                self.alpha_rebalance[alpha] = False
                
                alpha.compute_allocation(context, data)

                
################################### [9] Risk Manager ######################################

'''
Does what it says on the tin, this can be as simple or complex as desired, so long as it takes the input of a target porfolio and provides an output of a risk adjusted target porfolio in the same format as its input
'''
class RiskManagerPortfolio:

    def compute_risk(self, context, data, target_portfolio):
        
        #examine target portfolio considering market exposure and puported leverage
        #may enforce a scaling factor to shrink positions in order to keep target beta
        #down and volatility minimised
        self.target_portfolio = target_portfolio
        #CHECK FOR BAD DATA PRINTS IN ORDER TICKERS
        '''
        for stock in self.target_porfolio: #iterate through stocks in target_portfolio for errors
            
            prices = history(100, '1d', 'close_price').dropna(axis=1) #get last 100 days of stock price data drop NA's
            
            std = prices[stock].std() #getting std of stock

            if abs(prices[stock][-1] - prices[stock][-2]) > 10 * std:
                
                log("{0}: STD = {1}  Error in price data".format(stock.symbol,std)) #log the error
                #implement logic to remove this from order list and recalculate possibly?
        
        '''
        #getting the current portfolio value considering cash, this is basic measure to keep leverage under control
        target_percent_scaledown = max(context.portfolio.cash/context.portfolio.portfolio_value,1)
        
        for alloc in self.target_portfolio:

            alloc_alpha = self.target_portfolio[alloc] / target_percent_scaledown 

            self.target_portfolio[alloc] = alloc_alpha 
        
        self.risked_target_portfolio = self.target_portfolio #output updated target portfolio
            
            
################################ [10] Execution Handler ##################################

'''
Again very obvious section, this is section actions the requests of the rest of the algorithm and records the order in a log. Unfufilled orders are closed and noted here when computing orders. This may be something that could be enhanced or modified 
'''
class ExecutionHandlerMarket:

    def compute_orders(self, context, data, target_portfolio):
        
        for stock in context.securities: #this needs modifying from previous design
            
            if stock in target_portfolio:
                order_target_percent(stock, target_portfolio[stock])
                print("Symbol: {0}, Allocation requested = {1}".format(stock.symbol,target_portfolio[stock]))
            else:
                pass
            
            
###########################################################################################
###################################### END OF CODE ########################################
###########################################################################################

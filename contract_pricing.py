"""
Author: Kai Weterings
Date: 16/11/2023 (dd/mm/YYYY)

From: https://github.com/kweterings/Trader_Contract_Valuation_Script
"""

# All imported and files/scripts libraries here.
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import calendar
import math as mt
import numpy as np
import price_predict as pp

# This is a contract valuation automated program for clients interested in the market for natural gas. This valuation is
# based on price values determined by another pricing model program (import price_predict as pp). Please be aware that
# if the file has different name or isn't in the same working directory as this file, this script will not work.

# NOTE: Two key assumptions were made whilst writing this program;
#   1. When a client decides to perform an action (inject or withdraw), the total cost/earning is of the entire volume
# on that date, i.e. irrespective of the change in prices during the days of natural gas transport from and away.
#   2. The rate of injection or withdrawal are mutually exclusive; the rate at which gas is injected does not affect
# any natural gas being withdrawn, and vis-versa. The rate is currently the same for injection and withdrawal,
# however this can easily be changed.

# Furthermore, the natural gas prices from the pricing model script is in $/MMBtu. Hence, later multiplied
# by the total volumes bought or sold on that date. This may be different for other pricing models so make sure to
# adjust.

# Input parameters necessary for determining contract valuation: (change these to analyse new contracts).

# Date of natural gas injection in form %d/%m/%y, input as a string.
injection_dates = ['11/12/21', '13/12/21', '15/12/21', '17/12/21']
# Date of natural gas withdrawal in form %d/%m/%y, input as a string.
withdrawal_dates = ['14/12/21', '16/12/21', '18/12/21']
# Volume of natural gas injected (index must be same as index of corresponding date), in MMBtu.
injected_natural_gas_volumes = [100002, 100003, 700000, 100000]
# Volume of natural gas withdrawn (same index rule as above), in MMBtu.
withdrawn_natural_gas_volumes = [300000, 600005, 100000]
# The facility's rate of injection/withdrawal (MMBtu per day).
rate_of_injection_or_withdrawal = 50000
# The maximum natural gas, in MMBtu, that the facility can hold.
storage_max_capacity = 2000000
# The monthly cost of using the natural gas storage facility.
storage_facility_usage_cost = 100000
# Cost of injecting/withdrawing natural gas to/from the facility per 1 million MMBtu.
injection_withdrawal_cost = 10000
# Per transport of natural gas to and from the storage facility (any volume from one given client action).
cost_of_transport = 50000

# These meaning of these variables can be modified accordingly if not totally accurate for the type of contract this
# program is being used for.

# Altering the list values so they go chronologically.
all_original_dates = injection_dates + withdrawal_dates
withdrawn_natural_gas_volumes_negative = [- + elem for elem in withdrawn_natural_gas_volumes]  # - for removing volume.
all_original_volumes = injected_natural_gas_volumes + withdrawn_natural_gas_volumes_negative
all_dates = [datetime.strptime(date, '%d/%m/%y') for date in all_original_dates]
sorted_dates = sorted(all_dates)
sorted_dates_indices = sorted(range(len(all_dates)), key=lambda i: all_dates[i])  # Same order change as date list.
sorted_volumes = [all_original_volumes[i] for i in sorted_dates_indices]

# Checking if all provided dates have a corresponding volume value.
if len(sorted_volumes) != len(sorted_dates):
    print('The number of dates (injection or withdrawal) does not correspond to the number of volumes (injected or '
          'withdrawn) provided. Please fix this issue.')
    quit()

# Checking if some volume of natural gas is remaining after contract end, this should be 0 at contract end.
if mt.fsum(sorted_volumes) != 0:
    print('The client still has natural gas in the storage after the final contract date. This must be changed.')
    quit()

# Creating 2 lists: one for action duration and another for time between actions (dates).
action_durations = []  # In days.
number_of_days_between_successive_dates = []
for volume, date1, date2 in zip(sorted_volumes[:-1], sorted_dates[:-1], sorted_dates[1:]):
    days_until_completed_action = np.ceil(volume / rate_of_injection_or_withdrawal)
    days_between_actions = (date2 - date1).days
    action_durations.append(days_until_completed_action)
    number_of_days_between_successive_dates.append(days_between_actions)

# Checking if actions overlap, hence pushing back that action due to the injection/withdraw rate limit.
client_action_overlap = any(needed_days >= allowed_days for needed_days, allowed_days in
                            zip(action_durations, number_of_days_between_successive_dates))

if client_action_overlap:  # The volumes in the storage will be different over time if overlapped vs. not overlapped.
    # Sorting both injection and withdraw dates separately, chronologically, alongside corresponding volumes like above.
    injection_dates_formatted = [datetime.strptime(date, '%d/%m/%y') for date in injection_dates]
    sorted_injection_dates = sorted(injection_dates_formatted)
    sorted_injection_dates_indices = sorted(range(len(injection_dates_formatted)),
                                            key=lambda i: injection_dates_formatted[i])
    sorted_injection_volumes = [injected_natural_gas_volumes[i] for i in sorted_injection_dates_indices]

    withdrawal_dates_formatted = [datetime.strptime(date, '%d/%m/%y') for date in withdrawal_dates]
    sorted_withdraw_dates = sorted(withdrawal_dates_formatted)
    sorted_withdraw_dates_indices = sorted(range(len(withdrawal_dates_formatted)),
                                           key=lambda i: withdrawal_dates_formatted[i])
    sorted_withdraw_volumes = [withdrawn_natural_gas_volumes_negative[i] for i in sorted_withdraw_dates_indices]

    # Same 2 lists as above but for withdraw dates and volumes. Will be used to determine the days past the final
    # provided date at which the contract actually ends.
    withdraw_action_durations = []
    withdraw_number_of_days_between_successive_dates = []
    for volume, date1, date2 in zip(sorted_withdraw_volumes[:-1], sorted_withdraw_dates[:-1],
                                    sorted_withdraw_dates[1:]):
        days_until_completed_action = np.ceil(volume / rate_of_injection_or_withdrawal)
        days_between_actions = (date2 - date1).days
        withdraw_action_durations.append(days_until_completed_action)
        withdraw_number_of_days_between_successive_dates.append(days_between_actions)

    # Determining the extra days to the end of the contract beyond the first and last provided date.
    volume_left_to_withdraw = 0
    extra_needed_days = 0
    for needed_days, allowed_days, volume, date1, date2 in zip(withdraw_action_durations,
                                                               withdraw_number_of_days_between_successive_dates,
                                                               sorted_withdraw_volumes[:-1], sorted_withdraw_dates[:-1],
                                                               sorted_withdraw_dates[1:]):
        # Effective as if action days carry over it will take longer for all actions to be finished.
        effective_needed_days = abs(needed_days) + extra_needed_days
        if effective_needed_days >= allowed_days:
            extra_volume = abs(volume) - allowed_days * rate_of_injection_or_withdrawal  # Volume left after time of 2
            # adjacent dates.
            extra_needed_days += extra_volume / rate_of_injection_or_withdrawal  # Topping up other extra action days.
            last_date = date2
        else:
            volume_left_to_withdraw = 0
            extra_needed_days = 0

    # Making sure the last action was a withdrawal, it should be but this is simply validation.
    if sorted_volumes[-1] < 0:
        # Days needed for last action (withdrawal).
        extra_needed_days += abs(sorted_volumes[-1]) / rate_of_injection_or_withdrawal

    # During of the contract in days. Np.ceil if a float, simple making sure it doesn't affect rest of code.
    contract_length_in_days = int(np.ceil((sorted_dates[-1] - sorted_dates[0]).days + extra_needed_days))

    # Arrays 'injections' and 'withdrawals' will end up being made up of 0s and 1s: 0 being no action (volume moved) on
    # that day and 1 being an action is occurring on that day.
    injections = np.zeros(contract_length_in_days)
    injection_volumes_per_day = np.zeros(contract_length_in_days)
    withdrawals = np.zeros(contract_length_in_days)
    withdrawal_volumes_per_day = np.zeros(contract_length_in_days)
    day_index_array = np.arange(0, contract_length_in_days)

    date_of_first_action = sorted_injection_dates[0]

    # Will be used to create lists of the volume injected or withdrawn, every element being the volume per day.
    def divide_into_list(number, divisor):
        result = []
        while number >= divisor:
            result.append(divisor)
            number -= divisor

        if number != 0:
            result.append(number)

        return result

    # When using the lists of 0s and 1s (0s no action and 1s there being action on a given days' element), this function
    # will help pile action days on top of already present 1s instead of replace them.
    def find_next_zero(index_of_one, array):
        # Find the index of the next 0 after the first 1
        index_of_next_zero = index_of_one + np.argmax(array[index_of_one:] == 0)
        return index_of_next_zero

    # Necessary for when adding together volume_per_day arrays, so values less than the daily rate don't end up between
    # larger daily rate values for volumes moved in a day.
    def add_into_larger_array(larger_array, smaller_array, start_index):
        # Add smaller array values to larger array, with max value constraint
        remainder = 0
        for i in range(len(smaller_array)):
            temp_sum = larger_array[i + start_index] + smaller_array[i] + remainder
            larger_array[i + start_index] = min(temp_sum, rate_of_injection_or_withdrawal)
            remainder = max(0, temp_sum - rate_of_injection_or_withdrawal)

        # Add remaining remainder to the next element in the larger array
        if remainder > 0:
            for i in range(start_index + len(smaller_array), len(larger_array)):
                temp_sum = larger_array[i] + remainder
                larger_array[i] = min(temp_sum, rate_of_injection_or_withdrawal)
                remainder = max(0, temp_sum - rate_of_injection_or_withdrawal)
                if remainder == 0:
                    break

    # Will turn the above pre-made arrays for injections into the corresponding patterns for this contract. 0s and 1s
    # and volumes per day in each element.
    for date, volume in zip(sorted_injection_dates, sorted_injection_volumes):
        index1 = (date - date_of_first_action).days
        index2 = int(np.ceil(abs(volume) / rate_of_injection_or_withdrawal)) + index1  # np.ceil in case of decimal.
        # This will mean that there are no underestimations of the time taken to inject the total volume.
        divided_volumes_to_add = divide_into_list(abs(volume), rate_of_injection_or_withdrawal)
        if injections[index1] == 1:
            new_index1 = find_next_zero(index1, injections)
            new_index2 = index2 + (new_index1 - index1)
            injections[new_index1:new_index2] = 1
            add_into_larger_array(injection_volumes_per_day, divided_volumes_to_add, index1)
        else:
            injections[index1:index2] = 1
            injection_volumes_per_day[index1:index1 + len(divided_volumes_to_add)] = divided_volumes_to_add

    # Same as above but for withdrawals.
    for date, volume in zip(sorted_withdraw_dates, sorted_withdraw_volumes):
        index1 = (date - date_of_first_action).days
        index2 = int(np.ceil(abs(volume) / rate_of_injection_or_withdrawal)) + index1
        divided_volumes_to_add = divide_into_list(abs(volume), rate_of_injection_or_withdrawal)
        if withdrawals[index1] == 1:
            new_index1 = find_next_zero(index1, withdrawals)
            new_index2 = index2 + (new_index1 - index1)
            withdrawals[new_index1:new_index2] = 1
            add_into_larger_array(withdrawal_volumes_per_day, divided_volumes_to_add, index1)
        else:
            withdrawals[index1:index2] = 1
            withdrawal_volumes_per_day[index1:index1 + len(divided_volumes_to_add)] = divided_volumes_to_add

    current_volume_stored_to_date = 0  # Pre-set variable.
    # The final step for the if client_action_overlap condition, monitoring the daily evolution of the volume in the
    # storage. This will help check if any limits are surpassed, i.e. more than max capacity or withdrawing more than is
    # in the storage facility.
    for injection, withdrawal, injection_volume, withdraw_volume, delta_day in zip(injections, withdrawals,
                                                                                   injection_volumes_per_day,
                                                                                   withdrawal_volumes_per_day,
                                                                                   day_index_array):
        if injection == 1 and withdrawal == 1:  # On given day, injection and withdrawal. However, possible differed
            # amounts.
            current_volume_stored_to_date += injection_volume - withdraw_volume
        elif injection == 1 and withdrawal == 0:  # On given day, injection but no withdrawal.
            current_volume_stored_to_date += injection_volume
        elif injection == 0 and withdrawal == 1:  # On given day, withdrawal but no injection.
            current_volume_stored_to_date -= withdraw_volume

        if current_volume_stored_to_date > storage_max_capacity:  # If injecting more than possible.
            date_of_overflow = (sorted_dates[0] + timedelta(days=delta_day)).strftime('%d/%m/%y')
            print(f"On the contract date of {date_of_overflow} (dd/mm/yy) the storage capacity was exceeded. "
                  f"Hence the client has bought natural gas at this time than the storage can handle.\n"
                  f"Please adjust the values so this is no longer the case.")
            quit()
        elif current_volume_stored_to_date < 0:  # If withdrawing more than the client has.
            date_of_empty = (sorted_dates[0] + timedelta(days=delta_day)).strftime('%d/%m/%y')
            print(f"On the contract date of {date_of_empty} (dd/mm/yy) there was no more natural gas to withdraw. "
                  f"Hence the client attempted to withdraw more than they had available in the storage facility.\n"
                  f"Please adjust the values so this is no longer the case.")
            quit()

else:  # If client action does not overlap, this simple monitoring will suffice, i.e. same checks as above.
    for elem_index in range(len(sorted_volumes) + 1):
        total_volume = mt.fsum(sorted_volumes[:elem_index])
        if total_volume > storage_max_capacity:  # If injecting more than possible.
            too_large_injection = sorted_volumes[elem_index - 1]
            print(f'The injected volume of {too_large_injection} MMBtu made the clients total owned natural gas volume '
                  f'larger than the maximum storage capacity of {storage_max_capacity} MMBtu. '
                  f'Please adapt the values for this to no longer be the case.')
            quit()
        elif total_volume < 0:  # If withdrawing more than the client has.
            too_large_withdraw = str(sorted_volumes[elem_index - 1]).strip('-')
            print(f'The withdrawn volume of {too_large_withdraw} MMBtu is more than the client has stored at the time '
                  f'of withdrawal. Please adapt the values for this to no longer be the case.')
            quit()

    # Contract length is necessary later so will also need to be defined in the else: condition it is in.
    contract_length_in_days = ((sorted_dates[-1] - sorted_dates[0]).days +
                               (abs(sorted_volumes[-1]) / rate_of_injection_or_withdrawal))

# Preamble, intro to program for user.
print('Welcome to this contract valuation program for clients interested in the market for natural gas. Below will '
      'be the necessary information.\n')

total_prices = []
month_indices = []
# Looping through every date of client action to determine the cost or earnings of the client, whether injecting or
# withdrawing.
for date, volume in zip(sorted_dates, sorted_volumes):

    date_day = date.day
    date_month = date.month
    date_year = date.year
    days_in_injection_month = calendar.monthrange(date_year, date_month)[1]  # To be more precise, exact days in month.

    date_month_index = (date_day / days_in_injection_month) + (date_year - 2020) * 12 + (date_month - 1)
    month_indices.append(date_month_index)  # A month index to be used in the price prediction program. Will act as 'x'
    # variable in regression model based on data. January 1st 2020 has date_month_index 0.

    # Prices $/MMBtu for this pricing model used.
    price_at_date = pp.price_prediction(date_month_index)

    total_price_of_volume = price_at_date * volume  # Since price from model is dollar per MMBtu.
    total_prices.append(total_price_of_volume)

    # Formatting the price data into a readable way for the user to understand the cost and earnings of the client.
    original_date_format = date.strftime('%d/%m/%y')
    if original_date_format in injection_dates and volume > 0:  # Two conditions in case date occurs in both injections
        # and withdrawals dates list.
        print(f'The total price (amount client pays) of natural gas when INJECTING on the {original_date_format} is: '
              f'{str(round(total_price_of_volume, 2)).strip("-")}$ ({round(price_at_date, 2)}$ per MMBtu).')
    elif original_date_format in withdrawal_dates and volume < 0:  # Same reasoning as above for two conditions.
        print(f'The total price (amount client earns) of natural gas when WITHDRAWING on the {original_date_format} is:'
              f' {str(round(total_price_of_volume, 2)).strip("-")}$ ({round(price_at_date, 2)}$ per MMBtu).')

final_difference_in_price = round(mt.fsum(total_prices) * -1, 2)  # Total earnings of client pre extra cost inclusion.

print(f'\nThe final price difference (total withdraw price - total injection price), i.e. the money earned by the '
      f'client, is: {final_difference_in_price}$.')

# Used for part of the storage costs.
total_handled_natural_gas_by_facility = mt.fsum(injected_natural_gas_volumes + withdrawn_natural_gas_volumes)

# Finding contract length in months to determine the rental price of using storage facility, where any roll-over to
# another month will lead to another monthly rental payment to the facility.
date_difference = relativedelta(sorted_dates[-1], sorted_dates[0])
months_difference = date_difference.years * 12 + date_difference.months + 1

# This cost is calculated based on the variable defined at the beginning for given costs.
storage_cost = ((storage_facility_usage_cost * months_difference) +  # Storage usage cost, per month.
                (injection_withdrawal_cost * total_handled_natural_gas_by_facility / 1000000) +  # Cost per 1m MMBtu.
                (cost_of_transport * len(sorted_volumes)))  # Logistics cost per each time a client action occurs.

# Final contract valuation based on values calculated above.
contract_valuation = round(final_difference_in_price - storage_cost, 2)

# Final prints to show contract valuation and other information about the contract (length, start and end dates, etc...)
print(f'The total storage and logistics cost during the period of the contract is: {round(storage_cost, 2)}$.')
print('---------------------------')
print(f'After careful valuation, the contract valuation with all extra costs taken into account is: '
      f'{contract_valuation}$.')
print(f'This contract will span from the {sorted_dates[0].strftime("%d/%m/%y")} until the '
      f'{(sorted_dates[0] + timedelta(days=contract_length_in_days)).strftime("%d/%m/%y")} (contract ends when no '
      f'gas is left in the storage).')
print('Note: This valuation is based on price predictions of natural gas from a pricing model.')

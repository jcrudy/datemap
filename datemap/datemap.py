'''
Created on Nov 14, 2012

@author: jason
'''
import datetime
import interval


class _NegativeInfinity(object):
    def __init__(self):
        pass

    def timetuple(self):
        return tuple()
    
    def __lt__(self, other):
        if self == other:
            return False
        else:
            return True
        
    def __le__(self, other):
        return True
    
    def __gt__(self, other):
        return False
    
    def __ge__(self, other):
        if self == other:
            return True
        else:
            return False
        
    def __ne__(self, other):
        return not (self.__eq__(other))
    
    def __eq__(self, other):
        return isinstance(other,_NegativeInfinity)
    
    def __hash__(self):
        return hash(_NegativeInfinity)
    
    def __neg__(self):
        return eternity
_negativeInfinity = _NegativeInfinity()

class _Infinity(object):
    def __init__(self):
        pass
    
    def timetuple(self):
        return tuple()
    
    def __lt__(self, other):
        return False
    
    def __le__(self, other):
        return self == other or self < other
    
    def __gt__(self, other):
        if self != other:
            return True
        else:
            return False
        
    def __ge__(self, other):
        return True
        
    def __ne__(self, other):
        return not (self.__eq__(other))
    
    def __eq__(self, other):
        return isinstance(other,_Infinity)
    
    def __hash__(self):
        return hash(_Infinity)

    def __neg__(self):
        return _negativeInfinity
    
eternity = _Infinity()
    
class DateMap(object):
    def __init__(self, intervals):
        self.intervals = intervals
    
    @classmethod
    def from_tuples(cls, tuples):
        intervals = []
        for policy in tuples:
            intr = interval.Interval(policy[0],policy[1],lower_closed=True,upper_closed=False)
            intervals.append(intr)
        return cls(interval.IntervalSet(intervals))  #All intervals are [).  All methods assume [) intervals.
    
    def __or__(self, other):
        return self.__class__(self.intervals | other.intervals)
    
    def __and__(self, other):
        return self.__class__(self.intervals & other.intervals)
        
            
    
    def __sub__(self, other):
        return self.__class__(self.intervals - other.intervals)
    
    def __invert__(self):
        return DateMap.from_tuples([(-eternity,eternity)]) - self
    
    def __eq__(self, other):
        if other.__class__ is DateMap:
            return self.intervals == other.intervals
        else:
            return NotImplemented
    
    def split(self, max_gap):
        '''
        Split into multiple datemaps on any gap larger than max_gap.
        '''
        if not self.intervals:
            return self.__class__(interval.IntervalSet([]))
        current_upper = self.intervals[0].upper_bound
        current_lower = self.intervals[0].lower_bound
        result = []
        for interval in self.intervals.intervals[1:]:
            if (interval.lower_bound - current_upper).days > max_gap:
                result.append((current_lower, current_upper))
                current_lower = interval.lower_bound
            current_upper = interval.upper_bound
        result.append((current_lower, current_upper))
        return [self.truncate(lower, upper) for lower, upper in result]

    @property
    def lower_bound(self):
        return self.intervals[0].lower_bound
    
    @property
    def upper_bound(self):
        return self.intervals[-1].upper_bound
    
    def __contains__(self, date):
        return date in self.intervals
    
    
    def truncate(self, lower=-eternity, upper=eternity):
        '''Return a copy truncated above and/or below.'''
        return self & self.__class__(interval.IntervalSet([interval.Interval(lower_bound=lower,upper_bound=upper,upper_closed=False)]))
    
    def partition(self, partitions):
        assert sum(partitions) == self.period
        result = []
        lower = 0
        upper = 0
        for part in partitions:
            upper += part
            result.append(self.slice(lower, upper))
            lower = upper
        return result
    
    def slice(self, lower=0, upper=None):
        period = self.period
        if upper is None:
            upper = period
        if lower >= upper:
            return self.__class__(interval.IntervalSet([]))
        lower_date = self.date_of(lower)
        if upper == period:
            upper_date = self.date_of(upper-1) + datetime.timedelta(days=1)
        else:
            upper_date = self.date_of(upper)
        return self & self.__class__.from_tuples([(lower_date, upper_date)])
    
    @property
    def period(self):
        total = 0
        for intr in self.intervals.intervals:
            total += (intr.upper_bound - intr.lower_bound).days
        return total
    
    def __len__(self):
        return len(self.intervals)
    
    def delta_of(self, date):
        if date not in self:
            raise ValueError
        result = 0
        for intr in self.intervals.intervals:
            if date < intr.lower_bound:
                break
            result += (min(intr.upper_bound,date) - intr.lower_bound).days
        return datetime.timedelta(days=result)
        
        
#        if date <= self.lower_bound:
#            result = -1*(self.lower_bound - date).days
#        elif date >= self.upper_bound:
#            result = period + (date - self.upper_bound).days
#        else:
#            result = 0
#            for intr in self.intervals:
#                if date < intr.lower_bound:
#                    break
#                result += (min(intr.upper_bound,date) - intr.lower_bound).days
#        return datetime.timedelta(days=result)
    
    def date_of(self, day):
        if isinstance(day,datetime.timedelta):
            day = day.days
        period = self.period
        if day >= period or day < -1*period:
            raise IndexError
        if day < 0:
            day = day % period
        remaining = day
        for intr in self.intervals.intervals:
            result = intr.lower_bound
            duration = (intr.upper_bound - intr.lower_bound).days
            if remaining < duration:
                result += datetime.timedelta(days=remaining)
                break
            remaining -= duration
        return result

all_time = DateMap.from_tuples([(-eternity,eternity)])





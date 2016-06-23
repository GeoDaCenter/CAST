"""
Event handler for implementing brushing-linking between all widgets 
"""

__author__  = "Xun Li <xunli@asu.edu> "
__all__ = ['AbstractData','Event','EventHandler']

class AbstractData():
    """
    Generic data model for Event object
    """
    def __init__(self,parent):
        self.parent = parent
        self.layer_name = ''
        self.shape_ids = {} 
        self.boundary = []

    @property
    def layer_name(self):
        return self.layer_name
    
    @property
    def shape_ids(self):
        """
        a dict for shape_ids
        key: shape layer name
        value: [] a list of shape_ids
        """
        return self.shape_ids
    
    @property
    def boundary(self):
        return self.boundary
    
class Event():
    """
    Generic event to use with EventDispatcher.
    """
    def __init__(self, event_type, data=None):
        """
        The constructor accepts an event type as string and a custom data
        """
        self._type = event_type
        self._data = data
        
    @property 
    def type(self):
        return self._type
        
    @property
    def data(self):
        return self._data

    
class EventHandler():
    """
    Generic event dispatcher which listen and dispatch events
    """
    
    def __init__(self):
        self._events = dict()
        
    def __del__(self):
        """
        Remove all listener references at destruction time
        """
        self._events = None
    
    def has_listener(self, event_type, listener):
        """
        Return true if listener is register to event_type
        """
        # Check event type and for the listener
        if event_type in self._events.keys():
            return listener in self._events[ event_type ]
        else:
            return False
        
    def dispatch_event(self, event):
        """
        Dispatch an instance of Event class
        """
        # Dispatch the event to all the associated listeners 
        if event.type in self._events.keys():
            dead_listeners = []
            listeners = self._events[ event.type ]
            for listener in listeners:
                # prevent dispatch event to sender
                if event.data.parent != listener.__self__: 
                    try:
                        listener( event )
                    except:
                        dead_listeners.append(listener)
            # remove any deleted wxobject
            for listener in dead_listeners:
                self.remove_event_listener(event.type, listener)
        
    def add_event_listener(self, event_type, listener):
        """
        Add an event listener for an event type
        """
        # Add listener to the event type
        if not self.has_listener( event_type, listener ):
            listeners = self._events.get( event_type, [] )
            listeners.append( listener )
            self._events[ event_type ] = listeners
    
    def remove_event_listener(self, event_type, listener):
        """
        Remove event listener.
        """
        # Remove the listener from the event type
        if self.has_listener( event_type, listener ):
            listeners = self._events[ event_type ]
            
            if len( listeners ) == 1:
                # Only this listener remains so remove the key
                del self._events[ event_type ]
            else:
                # Update listeners chain
                listeners.remove( listener )
                
                self._events[ event_type ] = listeners
                

        
# platform.py
# author: Christophe VG

# Platform interface for the code emission

class Platform():
  
  def setup(self, unit):
    """
    Allows a platform to set up basic infrastructure.
    """
    return NotImplementedError, "setup(self, unit)"
  
  def type(self, type):
    """
    Used to map code.Type to platform specific type.
    """
    return NotImplementedError, "type(self, type)"

  def add_handler(self, event, call=None, module=None, location=None):
    """
    Used to register platform specific callbacks/handlers. Dispatches to
    other methods based on the required event to be handled.
    """
    return {
      "receive" : self.handle_receive
    }[event](call, module, location)

  def handle_receive(self, function=None, module=None, location=None):
    """
    Handle receive events, given a function to call and a possible location in
    the code where to add it. The latter can be ignored if no simple callback
    registration is used, but a direct call from other/framework code.
    """
    return NotImplementedError, "handle_receive(self, handler)"

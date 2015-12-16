
from .entity_message import *
from .entity_room import *
from .messenger import *
from .form import *
from .action import *
from .ws_action import *
from .hook import *
from .box import *
from .lazy import *
from .trigger import *

from .admin import *

@IN.hook
def template_path():
	me_path = os.path.dirname(os.path.abspath(__file__))
	return [{
		'path' : ''.join((me_path, os.sep, 'templates', os.sep)),
		'weight' : 5,
	}]

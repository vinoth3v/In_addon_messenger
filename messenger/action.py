from .page import *

@IN.hook
def actions():
	actns = {}
	
	actns['message'] = {
		'handler' : action_handler_page_message,
	}
	
	actns['message/friends/list'] = {
		'handler' : action_handler_message_friends_list,
	}
	
	return actns
	

import os

@IN.hook
def asset_prepare(context):
	
	if context.nabar.id and not context.request.ajax:
		
		context.asset.add_js('''
			require(['In', 'In_messenger'], function(messenger){
				//IN.trigger('dom', true);
			});
			''', 'messenger.js', 'inline', weight = 11)
		
		context.asset.add_css('/files/assets-messenger/css/messenger.css', 'messenger.css', weight = 11)
		
@IN.hook
def public_file_paths():
	
	return {
		'assets-messenger' : {
			'base_path' : os.path.join(IN.APP.app_path, 'addons/messenger/assets'),
		}
	}
	
@IN.hook
def notification_count(context):
	
	try:
		nabar_id = context.nabar.id
		
		if not nabar_id:
			return
			
		
		cursor = IN.db.select({
			'table' : ['message.message_nabar', 'mn'],
			'count_column' : 'distinct m.room_id',
			'join' : [
				['inner join', 'message.message', 'm', [
					['mn.message_id = m.id']
				]]
			],
			'where' : [
				['mn.nabar_id', nabar_id],
				['mn.status', 1],
				['m.status', '>=', 1],
			],
		}).execute_count()
		
		if cursor.rowcount == 0:
			return
		
		count = cursor.fetchone()[0]
		
		return {
			'message_count' : count
		}
	except Exception as e:
		IN.logger.debug()
		

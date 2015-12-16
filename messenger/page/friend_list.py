

def action_handler_message_friends_list(context, action, **args):
	
	message_friends_init_lister(context)
	
def message_friends_init_lister(context, container = None):
	
	nabar_id = context.nabar.id
	
	if not nabar_id:
		return

	
	pager = {
		'type' : 'PagerLoadMore',
		'data' : {
			'css' : ['auto-scrollspy-click'],
			'attributes' : {'data-i-scrollspy' : '{topoffset: 200, delay:800, repeat: true}'},
		},
		'append_type' : 'append',
	}

	lister = Object.new('ObjectLister', {
		'id' : 'message_friends_init_lister',
		'entity_type' : 'Nabar',
		'handler_prepare_objects' : message_friends_init_lister_prepare_objects,		
		'pager' : pager,
		'limit' : 10,
		'container' : container, # add list to self instead fo context output
		#'view_mode' : 'activity_notification',
		'url' : 'message/friends/list',
		'content_panel' : {
			'css' : ['i-nav i-nav-offcanvas']
		}
	})
	
	# handle the list
	lister.list()
	

def message_friends_init_lister_prepare_objects(lister):
	
	nabar_id = IN.context.nabar.id
	
	query = IN.db.select({
		'tables' : [['relation.relation_member', 'rm']],
		'columns' : ['n.id'],
		'join' : [
			['inner join', 'relation.relation', 'r', [['rm.relation_id = r.id']]],
			['inner join', 'account.nabar', 'n', [['rm.to_entity_id = n.id AND n.status > 0']]],
			['left join', 'log.nabar_active', 'no', [['rm.to_entity_id = no.nabar_id']]],
		],
		'where' : [
			['r.type', 'friend'],
			['r.relation_status', IN.relater.RELATION_STATUS_ACTIVE],
			['rm.from_entity_type', 'Nabar'],
			['rm.from_entity_id', nabar_id],
			['rm.to_entity_type', 'Nabar'],
			['n.status', '>', 0]
		],
		'limit' : 10,
		'order' : {'no.active' : 'DESC'}
	})
	
	limit = lister.limit
	
	if lister.current > 1:
		limit = [lister.current * limit - 1, limit]
		query.limit = limit
	
	cursor = query.execute()
	
	entitier =  IN.entitier
	content_panel = lister.content_panel
	
	if cursor.rowcount > 0:
		
		result = cursor.fetchall()
		
		entity_ids = []
		for r in result:				
			if r[0] not in entity_ids:
				entity_ids.append(r[0])
		
		entities = entitier.load_multiple(lister.entity_type, entity_ids)
		weight = 1
		for id in entity_ids: # keep order
			if id in entities:
				entity = entities[id]
				entity.weight = weight
				
				if lister.list_object_class:
					entity.css.append(lister.list_object_class)
				
				content_panel.add('MessageTrigger', {
					'nabar' : entity,
					'attributes' : {
						'data-nabar_id' : entity.id,
						'onclick' : 'UIkit.offcanvas.hide();',
						'css' : ['i-panel i-margin-small-bottom i-margin-small-top i-pointer']
					}
				})
				
				weight += 1
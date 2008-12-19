<?php

error_reporting(E_ALL);

// INCLUDES

set_include_path('../library' . PATH_SEPARATOR 
               . '../application' . PATH_SEPARATOR 
               . get_include_path());
  
require_once('Zend/Loader.php');

Zend_Loader::registerAutoload();

require_once('../application/functions.php');

// CONFIG - env-specific settings are selected by server name.
//   DB env is based on tokens in sever name, to provide flexible local vhost configurations...
//   Host: selects mysql.aashe.net if server contains the token 'aashe', localhost otherwise
//   DB  : selects aashe_stars unless server contains token 'dev' or 'stage'
//   -> override these defaults by modifying the host or dbname element in main.ini
$server=$_SERVER['SERVER_NAME'];
$dbHost = (stripos($server,'aashe')===false) ? 'localhost' : 'aashe';
$dbName = (stripos($server,'dev')===false) ? ((stripos($server,'stage')===false) ? 'prod' : 'stage') : 'dev';
$sections = array( 'config',
                   'dbhost.'.$dbHost,
                   'db.'.$dbName,
                   'xmlrpc.'.$_SERVER['SERVER_NAME']
                 );
$config = new Zend_Config_Ini('../config/main.ini', $sections); 

// ROUTES

$router = Zend_Controller_Front::getInstance()->getRouter();
$router->addConfig($config->routes);

// DATABASE

$db = Zend_Db::factory($config->database);
$db->setFetchMode(Zend_Db::FETCH_ASSOC);
// If we make the connection explicitly, we need special logic here to catch and handle any exceptions
//  (normal error handling won't work yet, since bootstrap is not complete)
// Instead, use a lazy connection, so the DB connect is done only when it is first required.
//    http://framework.zend.com/manual/en/zend.db.html#zend.db.adapter.connecting.getconnection
//$db->getConnection();

// REGISTRATION

Zend_Registry::set('config', $config);
Zend_Registry::set('db', $db);
Zend_Registry::set('dbEnv', $config->database->params->dbname . '@' . $config->database->params->host);

// LAYOUTS
    //define ("ROOT_DIR",$_SERVER['DOCUMENT_ROOT'].'/..');
    define('APP_DIR', dirname(__FILE__));
    Zend_Layout::startMvc(array('layoutPath' => realpath(APP_DIR).'/views/layouts'));

// FRONT CONTROLLER

$front = Zend_Controller_Front::getInstance();
$front->registerPlugin(new STARS_Plugin_Offline($config->env->offline));
$front->run('../application/controllers');

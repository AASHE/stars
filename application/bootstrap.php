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
//   DB env is based on first two words in sever name, to provide flexible local vhost configurations...
//   starstracker.* / dev.* / stage.* will use aashe.net server, and DB aashe_ / dev_aashe / stage_aashe_stars
//   stars.* / localhost.*  will use server localhost, and DB aashe_stars
//   ?.dev.* / ?.stage.*  will use server localhost, and DB dev_ / stage_aashe_stars
//   -> override these defaults by modifying the host or dbname element in main.ini
$dbHost = strtok($_SERVER['SERVER_NAME'],'.');
$dbName = strtok('.');
$sections = array( 'config',
                   'db.'.$dbName,
                   'db.'.$dbHost,
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
Zend_Registry::set('dbEnv', $config->database->env);

// LAYOUTS
    //define ("ROOT_DIR",$_SERVER['DOCUMENT_ROOT'].'/..');
    define('APP_DIR', dirname(__FILE__));
    Zend_Layout::startMvc(array('layoutPath' => realpath(APP_DIR).'/views/layouts'));

// FRONT CONTROLLER

$front = Zend_Controller_Front::getInstance();
$front->registerPlugin(new STARS_Plugin_Offline($config->env->offline));
$front->run('../application/controllers');

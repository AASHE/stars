<?php
/**
 * STARS/XmlRpc/Client.php
 *
 * @author J. Fall
 * @version 0.1
 * @package STARS
 */

/**
 * STARS_XmlRpc_Client
 *
 * Extended XmlRpc Client services for STARS
 *   -configuration settings loaded from config->xmlrpc
 * Provides access to remote procedure calls,
 *  primarily inteded for use with the Drupal Resource Center
 * Each of the methods may throw several types of Zend_XmlRpc_Client_FaultException if something goes wrong,
 *   however server issue exceptions are trapped and re-thrown as a STARS_ErrorTicket
 */
class STARS_XmlRpc_Client extends Zend_XmlRpc_Client
{
    protected $_sessionid;   // the sessionid retrieved during authentication.
    protected $_xmlrpc;      // the xmlrpc configuration settings used by this client.
    
    /**
     * Construct a new XmlRpc Client.
     * @param $server  string URL for server or null for default server
     */
    public function __construct($server=null)
    {
        $this->_xmlrpc = Zend_Registry::get('config')->xmlrpc;

        if ($server == null) {
            $server = $this->_xmlrpc->default_server;
        }
        parent::__construct($server);
        $this->_sessionid = Zend_Session::getId();
    }

    /**
     * Authenticate to the server with given info.
     *
     * @param $username string User's login id on the server
     * @param $password string User's p/w on the server
     *
     * @return RPC result returned by server
     */
    public function login($username, $password)
    {
        $result = $this->call('user.login', array($username, $password));
        if ($this->_xmlrpc->use_sessid) {
            $this->_sessionid = $result['sessid'];
        }
        return $result['user'];
    }

    /**
     * Logout this client's session from the remote server.
     *
     * @return RPC result returned by server
     */
    public function logout()
    {
        return $this->call('user.logout', array());
    }

    /**
     * Get info about a user.
     *
     * @param $user string User's login name or user id on the server
     *
     * @return RPC result returned by server
     */
    public function getUser($user)
    {
        if (is_numeric($user)) {
            return $this->call('user.get', array((int)$user));
        }
        else {
            return $this->call('user.get-byname', array($user));
        }
    }

    /**
     * Get list of users based on their role.
     *
     * @param $role string  STARS_user or STARS_admin
     *
     * @return RPC result returned by server
     */
    public function getUsersByRole($role)
    {
        return $this->call('user.listbyrole', array($role));
    }

    /**
     * Get list of users based on their user name.
     *
     * @param $name string  first few characters in user's name
     *
     * @return RPC result returned by server
     */
    public function getUsersByName($name)
    {
        return $this->call('user.get-listbyname', array($name));
    }


    /**
     * Helper: make the RPC call and return the results.
     *         Traps HttpException and re-throws a STARS_ErrorTicket
     *
     * @param $function string name of the RPC function to be called.
     * @param $args     array of arguments to the RPC
     *
     * @return RPC result returned by server
     * @throws STARS_ErrorTicket if an server error occurred, Zend_XmlRpc_Client_FaultException for other errors.
     */
    public function call($function, $args)
    {
        $params = $this->_getParams($function);
         
        $params  = array_merge($params, $args);
         
        try {
            return parent::call($function, $params);
        }
        catch (Zend_XmlRpc_Client_HTTPException $e) {
            watchdog('XML-RPC', "HTTP request to XMLRPC  remote server failed. [{$e->getMessage()}]", WATCHDOG_ERROR);
            throw new STARS_ErrorTicket("Unable to connect to remote server - please try again later.",
            null, true);
        }
         
    }

    /**
     * Helper:  set-up the parameters for the RPC
     *
     * @param $function string name of the RPC function to be called.
     * @return the basic array of parameters required to make any RPC
     */
    private function _getParams($function)
    {
        if ($this->_xmlrpc->use_key) {
            $thisServer = $_SERVER['SERVER_NAME'];
            $timestamp = ''.time();
            srand();
            $nonce = md5( uniqid( rand(), true ) );

            $hash_parameters = array($timestamp, $thisServer, $nonce, $function);
            $hash = hash_hmac("sha256", implode(';', $hash_parameters), $this->_xmlrpc->key);
            $params = array(
                            $hash,
                            $thisServer,
                            $timestamp,
                            $nonce,
                           );
        }
        else {
            $params = array();
        }
        if ($this->_xmlrpc->use_sessid) {
            $params[] = $this->_sessionid;
        }
        return $params;
    }
}
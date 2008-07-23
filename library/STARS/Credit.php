<?php
/**
 * Stars Credit
 *
 * @category Model
 * @package STARS
 * @author  J. Fall
 */
 
/**
 * STARS_Credit
 * Domain Model representing a Stars Credit.
 * Also acts as a DB Mapper for the credits table.
 */
class STARS_Credit
{
  private $_record;
  private $_creditOID;

  /**
   * Construct a new Credit for the persistent object
   * @param integer $creditId  POID for the credit to construct
   */
  public function __construct($creditId)
  {
    $this->_creditOID = intval($creditId);
    $this->_record = null;  // using lazy read
  }

  /**
   * Is this Credit specified?
   * @return true if the Credit has a definition, false otherwise
   */
  public function isValidCredit()
  {
    $credit = $this->getCreditInfo();
    return ( count($credit) > 0 );
  }

  /**
   * Get the Persistent Object ID for this Credit
   * @return integer POID or null
   */
  public function getId()
  {
    $credit = $this->getCreditInfo();
    return $credit['creditid'];
  }

  /**
   * Get the points available for this Credit
   * @return integer points available or null
   */
  public function getPointsAvailable()
  {
    $credit = $this->getCreditInfo();
    return $credit['pointsavailable'];
  }

  /**
   * Get the title for this Credit 
   * @return string  (e.g., "Credit AF6" or "Prerequisit OP1")
   */
  public function getTitle()
  {
    if($this->isValidCredit()) {
      return ($this->isPrereq() ?
            ("Prerequisite ".$this->_record['creditnumber']) :
            ("Credit  ".$this->_record['sectionabbr'].$this->_record['creditnumber']))
          . ': ' . $this->_record['creditname'];
    }

    return '';
  }
  
  /**
   * Get information about this credit's section
   *  Required b/c Section is a Transaction Script object rather than a Domain Model.
   * @return array of strings describing the section ('id', 'title')
   */
  public function getSectionInfo()
  {
    return array(
                 'id' => $this->getSectionID(),
                 'title' => $this->getSectionTitle(),
                );
  }

  /**
   * Get Category ID for this Credit
   * @return integer
   */
  public function getSectionId()
  {
    $credit = $this->getCreditInfo();
    return $credit['dicreditcategory'];
  }

  /**
   * Get the section title for this Credit 
   * @return string  (e.g., "Adiministration and Finance")
   */
  public function getSectionTitle()
  {
    if($this->isValidCredit()) {
      return $this->_record['sectiontitle'];
    }
    return '';
  }


  /**
   * Is this Credit actually a pre-requisite?
   * @return true if it is a pre-req, false otherwise
   */
  public function isPrereq()
  {
    if($this->isValidCredit()) {
      return $this->_record['prerequisite'];
    }

    return '';
  }

  /**
   * Get the record for this Credit PDO
   * @return array with DB fields as keys, or empty array
   */
  public function getCreditInfo()
  {
    // Lazy read - load here if credit info not loaded yet.
    if ($this->_record == null) {
      $this->_record = $this->_retrieveRecord($this->_creditOID);
    }

    if ( $this->_isValidRecord($this->_record) ) {
      return $this->_record;
    }
    else {
      return array();
    }
  }

  /**
   * Helper: is the credit record valid for this PDO?
   * @param array $credit data array for a credit.
   */
  private function _isValidRecord($record)
  {
    return (is_array($record)  && 
            $record['creditid'] == $this->_creditOID );
  }


  // @TO DO: the functions are supplied as object and static method b/c
  //         Transaction Script code doesn't work with objects - that should change.
  /**
   * Build the form file name for this credit's PDF form.
   * @return string filename (NOT full path) for the PDF form for this credit.
   */
  public function formFilename()
  {
    $filename = $this->creditCode('_') . '.pdf';
    return $filename;
  }
  /**
   * Build the form file name for this credit's PDF form.
   * @return string filename (NOT full path) for the PDF form for this credit.
  */
  static public function getFormFilename($creditRecord)
  { 
    $filename = self::buildCreditCode($creditRecord,'_') . '.pdf';
    return $filename;
  }

  /**
   * Return a string that uniquely encodes this credit/category.
   * @param string seperator - character to use to seperate elements ('_'or ' ')
   * @return string that identifies this Credit (e.g., AF_C6)
   *         or '' if the credit does not exist.
   */
  public function creditCode($seperator = '_')
  {
    return self::buildCreditCode( $this->getCreditInfo(), $seperator );
  }
  /**
   * Helper - form the credit code from a record of data.
   * @return string that identifies this Credit (e.g., AF_C6)
   *         or '' if the credit does not exist.
   */
  static public function buildCreditCode($record, $seperator = '_')
  {
    $creditNumber = $record['creditnumber']<10?'0':'';
    $creditNumber .= $record['creditnumber'];
    $creditCode = $record['sectionabbr'] . $seperator .
                 ($record['prerequisite'] ? 'Prereq' : 'Credit') . $seperator .
                  $creditNumber;
    /* Rationalized conventions - now there is only one - the one above!
    $creditCode = $record['sectionabbr'].'_'.
                 ($record['prerequisite']?'P':'C').
                  $record['creditnumber'];
    */
    return $creditCode;
  }
  /**
   * Return a string that uniquely encodes the credit/category.
   * @return string that identifies this Credit (e.g., AF_Credit_06)
   *         or '' if the credit does not exist.
   */
  static public function getCreditCode($creditId)
  {
    $creditCode = '';
    try {
      $credit = Zend_Registry::get('db')->fetchAll
      (
        'SELECT c.*, di1.itemvalue AS sectionabbr
         FROM credits AS c
         INNER JOIN (dataitems AS di1)
         ON (c.dicreditcategory = di1.itemid)
         WHERE c.creditid = ?',
         array($creditId),
         Zend_Db::FETCH_ASSOC
      );

      if (count($credit) > 0) {
        $creditCode = self::buildCreditCode($credit[0]);
      }
    }

    catch(Zend_Db_Exception $e) { return '';}

    return $creditCode;
  }

  /**
   * Helper: retrieve one record from the DB representing this Credit
   * @param integer $creditId POID for the record to retrieve
   * @return array containing the record, with DB fields as keys
   *         or null if DB operation failed.
   * @todo improve error handling.
   */
  private function _retrieveRecord($creditId)
  {
    try {
      $credit = Zend_Registry::get('db')->fetchAll
      (
        'SELECT c.*, di1.itemdisplay AS sectiontitle, di1.itemvalue AS sectionabbr, di2.itemdisplay AS subsectiontitle
         FROM credits AS c
         INNER JOIN (dataitems AS di1)
         ON (c.dicreditcategory = di1.itemid)
         LEFT JOIN (dataitems AS di2)
         ON (c.dicreditsubcategory = di2.itemid)
         WHERE c.creditid = ?',
         array( $creditId),
         Zend_Db::FETCH_ASSOC
      );

      if (count($credit) > 0) {
        return $credit[0];
      }
      else {
        return null;
      }
    }

    catch(Zend_Db_Exception $e) { return null;}
  }

  /**
   * Fectch all the credits.
   * @return an array containing all credits (as STARS_Credit objects)
   *         or empty array if no credits exist.
   */
  static public function getAllCredits()
  {
    try {
      $creditRecs = Zend_Registry::get('db')->fetchAll
      (
        'SELECT c.*, di1.itemdisplay AS sectiontitle, di1.itemvalue AS sectionabbr, di2.itemdisplay AS subsectiontitle
         FROM credits AS c
         INNER JOIN (dataitems AS di1)
         ON (c.dicreditcategory = di1.itemid)
         LEFT JOIN (dataitems AS di2)
         ON (c.dicreditsubcategory = di2.itemid)',
         array(),
         Zend_Db::FETCH_ASSOC
      );

      // to do: this is O/R mapping layer stuff!
      $credits = array();
      foreach ($creditRecs as $rec) {
        $credit = new STARS_Credit($rec['creditid']);
        $credit->_record = $rec;
        $credits[] = $credit;
      }
      return $credits;
    }
    catch(Zend_Db_Exception $e) { return null;}
  }
}

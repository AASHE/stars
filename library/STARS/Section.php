<?php

class STARS_Section
{
    private $_credits = array();
    private $_sectionId;
    
    public function __construct($sectionId)
    {
        $this->_sectionId = intval($sectionId);
        
        $this->_retrieveCredits();
    }
    
    public function getCredits()
    {
        return $this->_credits;
    }
    
    public function getTitle()
    {
        if(count($this->_credits) > 0)
        {
            return $this->_credits[0]['sectiontitle'];
        }
        
        return '';
    }
    
    private function _retrieveCredits()
    {
        try
        {
            $this->_credits = Zend_Registry::get('db')->fetchAll
            (
                'SELECT o.*, c.*, di1.itemdisplay AS sectiontitle, di1.itemvalue AS sectionabbr, di2.itemdisplay AS subsectiontitle
                FROM credits AS c
                INNER JOIN (dataitems AS di1)
                ON (c.dicreditcategory = di1.itemid)
                LEFT JOIN (dataitems AS di2)
                ON (c.dicreditsubcategory = di2.itemid)
                LEFT JOIN (orgcreditdata AS o)
                ON (c.creditid = o.creditid AND o.orgid = ?)
                WHERE c.dicreditcategory = ?
                ORDER BY prerequisite DESC, creditnumber ASC',
                array(STARS_Person::getInstance()->get('orgid'), $this->_sectionId),
                Zend_Db::FETCH_ASSOC
            );
        }
        
        catch(Zend_Db_Exception $e) {}
    }
}

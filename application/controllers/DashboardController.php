<?php

class DashboardController extends STARS_ActionController
{
    public function indexAction()
    {
        $this->_protect(1);
        
        if(STARS_Person::getInstance()->get('level') > 1)
        {
            $this->_admin();
        }
        
        else
        {
            $this->_normalUser();
        }
    }
    
    private function _admin()
    {
        $this->view->script = '../application/views/scripts/dashboard/index.admin.phtml';
    }
    
    private function _normalUser()
    {
        $this->view->script = '../application/views/scripts/dashboard/index.normalUser.phtml';
    }
}

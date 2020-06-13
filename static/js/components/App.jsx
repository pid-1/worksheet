import React, { Suspense, useState }     from 'react';
import { BrowserRouter, Route, Switch }  from 'react-router-dom';
//import fileDownload                    from 'js-file-download';

// Non-Route components
import NavBar   from './NavBar';
import SignIn   from './SignIn';

// Routes:
import Home     from './Home';
import Managers from './Managers';
import Updates  from './Updates';
import Settings from './Settings';
import NotFound from './NotFound';

// For some reason, trying to prefetch with ...
//    /* webpackPrefetch: true */
// will cause it to pull twice:
//    - Once after loading the regular bundle, and
//    - Again when you navigate to Worksheet page
//
const Worksheet = React.lazy(() =>
   import(/* webpackChunkName: 'worksheet' */ './Worksheet')
);

import './css/App.css';


const App = () => {
   const [view, setView] = useState('depot');
   const [theme, setTheme] = useState('ag-theme-balham');
   const [isAuthenticated, setIsAuthenticated] = useState(false);


   if (! isAuthenticated) {
      return (
         <div className='container-form'>
            <SignIn
               setIsAuthenticated={setIsAuthenticated}
               setView={setView}
               setTheme={setTheme}
            />
         </div>
      )
   } else {
      return (
         <BrowserRouter>

            <NavBar />
            <Suspense fallback={<h3><br/> Loading ... </h3>}>

            <Switch>
               <Route exact path='/'          component={Home} />
               <Route exact path='/updates'   component={Updates} />
               <Route exact path='/managers'  component={Managers} />

               <Route exact path='/worksheet'
                  render={props => <Worksheet {...props}
                                       view={view}
                                       theme={theme} />}
               /> 

               <Route exact path='/settings'
                  render={props => <Settings {...props}
                                       setView={setView}
                                       setTheme={setTheme} />}
               /> 

               <Route component={NotFound} />
            </Switch>

            </Suspense>
         </BrowserRouter>
      )
   }
};

export default App;

import React, { createContext, useState } from 'react';

// this is the equivalent to the createStore method of Redux
// https://redux.js.org/api/createstore

// const [databases, setDatabases] = useState([])
let schemaData = {}
const updateSchemaData = x => schemaData = x

export const GlobalContext = createContext();

export const GlobalContextProvider = ({ children }) => {
	return (
		<GlobalContext.Provider value={{schemaData, updateSchemaData}} >
			{children}
		</GlobalContext.Provider>
		)
}

// export default { GlobalContext, GlobalContextProvider };
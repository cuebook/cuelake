import React, { createContext, useState } from 'react';

// this is the equivalent to the createStore method of Redux
// https://redux.js.org/api/createstore

// let metastoreTables = {}
// const updateMetastoreTables = x => metastoreTables = x

export const GlobalContext = createContext();

export const GlobalContextProvider = ({ children }) => {
	const [metastoreTables, setMetastoreTables] = useState({});
	const value = { metastoreTables, setMetastoreTables };

	return (
		<GlobalContext.Provider value={value} >
			{children}
		</GlobalContext.Provider>
	)
}

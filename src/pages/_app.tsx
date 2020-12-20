import { AppProps } from 'next/app'

import '../styles/global.css'

function App({ Component, pageProps}: AppProps) {
// export default function App({ Component, pageProps }) {
    return <Component {...pageProps} />
}

export default App
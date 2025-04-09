import { AppProps } from 'next/app';
import { QueryClient, QueryClientProvider } from 'react-query';
import '../styles/globals.css';

// Create a client for React Query
const queryClient = new QueryClient();

/**
 * Custom App component to initialize pages with global context
 */
function MyApp({ Component, pageProps }: AppProps) {
  return (
    <QueryClientProvider client={queryClient}>
      <Component {...pageProps} />
    </QueryClientProvider>
  );
}

export default MyApp; 
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import config from './config';
import { PlusIcon, ArrowDownTrayIcon } from '@heroicons/react/24/outline';

// Main application component for Writer Reports
// This will trigger the initial deployment to create gh-pages branch

interface Writer {
  id: string;
  name: string;
  articles: number;
  views: number;
  avg_views: number;
}

interface Summary {
  total_writers: number;
  total_articles: number;
  total_views: number;
  avg_views_per_article: number;
}

interface WriterData {
  writers: Writer[];
  summary: Summary;
}

function App() {
  const [data, setData] = useState<WriterData | null>(null);
  const [newWriterName, setNewWriterName] = useState('');
  const [isAddingWriter, setIsAddingWriter] = useState(false);
  const [isUpdatingWriter, setIsUpdatingWriter] = useState(false);
  const [selectedWriter, setSelectedWriter] = useState<Writer | null>(null);
  const [updateArticles, setUpdateArticles] = useState('');
  const [updateViews, setUpdateViews] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const response = await axios.get<WriterData>(`${config.apiUrl}/writers`);
      setData(response.data);
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  };

  const addWriter = async () => {
    try {
      await axios.post(`${config.apiUrl}/writers`, { name: newWriterName });
      setNewWriterName('');
      setIsAddingWriter(false);
      fetchData();
    } catch (error) {
      console.error('Error adding writer:', error);
    }
  };

  const updateStats = async (writerId: string, articles: number, views: number) => {
    try {
      await axios.put(`${config.apiUrl}/writers/${writerId}`, { articles, views });
      fetchData();
    } catch (error) {
      console.error('Error updating stats:', error);
    }
  };

  const exportReport = async () => {
    if (!startDate || !endDate) {
      alert('Please select both start and end dates');
      return;
    }

    try {
      const response = await axios.post(
        `${config.apiUrl}/export`,
        {
          start_date: startDate,
          end_date: endDate
        },
        { responseType: 'blob' }
      );
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'writer-report.png');
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (error) {
      console.error('Error exporting report:', error);
    }
  };

  const deleteWriter = async (writerId: string) => {
    if (window.confirm('Are you sure you want to delete this writer?')) {
      try {
        await axios.delete(`${config.apiUrl}/writers/${writerId}`);
        fetchData();
      } catch (error) {
        console.error('Error deleting writer:', error);
      }
    }
  };

  if (!data) return <div className="flex items-center justify-center min-h-screen">Loading...</div>;

  const { summary, writers } = data;

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8 space-y-4">
          <div className="flex justify-between items-center">
            <h1 className="text-3xl font-bold text-gray-900">Writer Reports</h1>
            <button
              onClick={() => setIsAddingWriter(true)}
              className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
            >
              <PlusIcon className="-ml-1 mr-2 h-5 w-5" />
              Add Writer
            </button>
          </div>
          
          <div className="bg-white p-4 rounded-lg shadow space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="block text-sm font-medium text-gray-700">Start Date</label>
                <input
                  type="date"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm text-sm"
                />
              </div>
              <div className="space-y-2">
                <label className="block text-sm font-medium text-gray-700">End Date</label>
                <input
                  type="date"
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm text-sm"
                />
              </div>
            </div>
            <button
              onClick={exportReport}
              disabled={!startDate || !endDate}
              className="w-full sm:w-auto inline-flex items-center justify-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <ArrowDownTrayIcon className="-ml-1 mr-2 h-5 w-5" />
              Export Report
            </button>
          </div>
        </div>

        {/* Stats Summary */}
        <div className="grid grid-cols-1 gap-5 sm:grid-cols-4 mb-8">
          {[
            { label: 'Total Writers', value: summary.total_writers },
            { label: 'Total Articles', value: summary.total_articles },
            { label: 'Total Views', value: summary.total_views.toLocaleString() },
            { label: 'Avg Views/Article', value: summary.avg_views_per_article },
          ].map((stat) => (
            <div key={stat.label} className="bg-white overflow-hidden shadow rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <dt className="text-sm font-medium text-gray-500 truncate">{stat.label}</dt>
                <dd className="mt-1 text-3xl font-semibold text-gray-900">{stat.value}</dd>
              </div>
            </div>
          ))}
        </div>

        {/* Writers List/Table */}
        <div className="space-y-4 sm:space-y-0">
          {/* Mobile View - Card Layout */}
          <div className="sm:hidden space-y-4">
            {writers.map((writer, index) => (
              <div key={writer.id} className="bg-white shadow rounded-lg p-4">
                <div className="flex justify-between items-start mb-4">
                  <div className="text-lg font-medium text-gray-900">
                    {`${index + 1}. ${writer.name}`}
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => {
                        setSelectedWriter(writer);
                        setUpdateArticles(writer.articles.toString());
                        setUpdateViews(writer.views.toString());
                        setIsUpdatingWriter(true);
                      }}
                      className="text-blue-600 hover:text-blue-900"
                    >
                      Update
                    </button>
                    <button
                      onClick={() => deleteWriter(writer.id)}
                      className="text-red-600 hover:text-red-900"
                    >
                      Delete
                    </button>
                  </div>
                </div>
                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <div className="text-sm font-medium text-gray-500">Articles</div>
                    <div className="mt-1 text-sm text-gray-900">{writer.articles}</div>
                  </div>
                  <div>
                    <div className="text-sm font-medium text-gray-500">Views</div>
                    <div className="mt-1 text-sm text-gray-900">{writer.views.toLocaleString()}</div>
                  </div>
                  <div>
                    <div className="text-sm font-medium text-gray-500">Avg Views</div>
                    <div className="mt-1 text-sm text-gray-900">{writer.avg_views}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Desktop View - Table Layout */}
          <div className="hidden sm:block bg-white shadow rounded-lg">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Writer</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Articles</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Views</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Avg Views</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {writers.map((writer, index) => (
                  <tr key={writer.id}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">
                        {`${index + 1}.`} {writer.name}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{writer.articles}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{writer.views.toLocaleString()}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{writer.avg_views}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <button
                        onClick={() => {
                          setSelectedWriter(writer);
                          setUpdateArticles(writer.articles.toString());
                          setUpdateViews(writer.views.toString());
                          setIsUpdatingWriter(true);
                        }}
                        className="text-blue-600 hover:text-blue-900 mr-4"
                      >
                        Update
                      </button>
                      <button
                        onClick={() => deleteWriter(writer.id)}
                        className="text-red-600 hover:text-red-900"
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Update Writer Modal */}
        {isUpdatingWriter && selectedWriter && (
          <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-lg p-4 sm:p-6 max-w-sm w-full mx-4 sm:mx-auto">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Update Writer Stats</h3>
              <div className="space-y-4">
                <div>
                  <label htmlFor="articles" className="block text-sm font-medium text-gray-700 mb-1">
                    Articles
                  </label>
                  <input
                    type="number"
                    id="articles"
                    value={updateArticles}
                    onChange={(e) => setUpdateArticles(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm text-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div>
                  <label htmlFor="views" className="block text-sm font-medium text-gray-700 mb-1">
                    Views
                  </label>
                  <input
                    type="number"
                    id="views"
                    value={updateViews}
                    onChange={(e) => setUpdateViews(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm text-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
              </div>
              <div className="mt-4 flex flex-col sm:flex-row justify-end space-y-2 sm:space-y-0 sm:space-x-3">
                <button
                  onClick={() => setIsUpdatingWriter(false)}
                  className="w-full sm:w-auto px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  onClick={() => {
                    updateStats(selectedWriter.id, parseInt(updateArticles), parseInt(updateViews));
                    setIsUpdatingWriter(false);
                  }}
                  className="w-full sm:w-auto px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700"
                >
                  Update
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Add Writer Modal */}
        {isAddingWriter && (
          <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center p-4">
            <div className="bg-white rounded-lg p-6 max-w-sm w-full mx-auto">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Add New Writer</h3>
              <input
                type="text"
                value={newWriterName}
                onChange={(e) => setNewWriterName(e.target.value)}
                placeholder="Writer name"
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 text-base"
              />
              <div className="mt-4 flex justify-end space-x-3">
                <button
                  onClick={() => setIsAddingWriter(false)}
                  className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  onClick={addWriter}
                  disabled={!newWriterName.trim()}
                  className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 disabled:opacity-50"
                >
                  Add
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;

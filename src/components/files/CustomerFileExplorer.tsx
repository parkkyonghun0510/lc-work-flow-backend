'use client';

import { useState, useMemo } from 'react';
import { useFiles, useDeleteFile, useDownloadFile, useCustomers, useApplicationsByCustomer, useApplications, useApplicationFiles } from '@/hooks/useFiles';
import { useFolders } from '@/hooks/useFolders';
import { useAuth } from '@/hooks/useAuth';
import { File, User, CustomerApplication } from '@/types/models';
import {
  FolderIcon,
  HomeIcon,
  ChevronRightIcon,
  MagnifyingGlassIcon,
  UserIcon,
  DocumentTextIcon,
  TrashIcon,
  ArrowDownTrayIcon,
  Squares2X2Icon,
  ListBulletIcon,
  ArrowPathIcon
} from '@heroicons/react/24/outline';
import { formatBytes, formatDate } from '@/lib/utils';
import FilePreview from './FilePreview';
import ImageThumbnail from './ImageThumbnail';
import ConfirmDialog from '@/components/ui/ConfirmDialog';

interface CustomerFolder {
  id: string;
  name: string;
  type: 'customer';
  customer_id: string;
  application_count: number;
  file_count: number;
  created_at: string;
}

interface ApplicationFolder {
  id: string;
  name: string;
  type: 'application';
  application_id: string;
  customer_id: string;
  file_count: number;
  status?: string;
  account_id?: string;
  created_at: string;
}

interface DocumentFolder {
  id: string;
  name: string;
  type: 'folder';
  application_id?: string;
  parent_id?: string;
  file_count: number;
  created_at: string;
}

interface FileItem extends File {
  type: 'file';
}

type ExplorerItem = CustomerFolder | ApplicationFolder | DocumentFolder | FileItem;

interface CustomerFileExplorerProps {
  onFileSelect?: (file: File) => void;
  selectable?: boolean;
  showActions?: boolean;
}

type ViewMode = 'grid' | 'list';

export default function CustomerFileExplorer({
  onFileSelect,
  selectable = false,
  showActions = true
}: CustomerFileExplorerProps) {
  const { user } = useAuth();
  const [currentPath, setCurrentPath] = useState<string[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [viewMode, setViewMode] = useState<ViewMode>('grid');
  const [selectedItems, setSelectedItems] = useState<Set<string>>(new Set());
  const [previewFile, setPreviewFile] = useState<File | null>(null);
  const [previewFiles, setPreviewFiles] = useState<File[]>([]);
  const [currentPreviewIndex, setCurrentPreviewIndex] = useState(0);
  const [fileToDelete, setFileToDelete] = useState<File | null>(null);

  // Get current context for API calls
  const currentCustomerId = currentPath.length > 0 ? currentPath[0] : undefined;
  const currentApplicationId = currentPath.length > 1 ? currentPath[1] : undefined;
  const currentFolderId = currentPath.length > 2 ? currentPath[2] : undefined;
  // Avoid sending virtual group ids to the API as folder_id
  const isVirtualGroup = currentFolderId?.startsWith('group:') || false;
  const effectiveFolderId = isVirtualGroup ? undefined : currentFolderId;

  const { data: filesData, isLoading, refetch } = useFiles({
    // Only fetch files when we're inside a specific path
    application_id: currentApplicationId,
    folder_id: effectiveFolderId,
    limit: 100,
  });

  const deleteFileMutation = useDeleteFile();
  const { downloadFile } = useDownloadFile();

  // Real data: customers and applications with file counts
  const { data: customersData, isLoading: isLoadingCustomers } = useCustomers({ page: 1, size: 100 });
  const { data: applicationsList = [], isLoading: isLoadingApplications } = useApplicationsByCustomer(currentCustomerId || '');
  const { data: foldersData = [], isLoading: isLoadingFolders } = useFolders({
    application_id: currentApplicationId,
    parent_id: effectiveFolderId,
  });
  
  // Get files for the current application or folder
  const { data: applicationFilesData, isLoading: isLoadingApplicationFiles } = useApplicationFiles(
    currentApplicationId || '',
    { page: 1, size: 100 }
  );

  // Aggregate data for counts at the customer and application levels
  // Fetch all applications and files (bounded size) to compute counts
  const { data: allApplicationsData } = useApplications({ page: 1, size: 1000 });
  const { data: allFilesData } = useFiles({ page: 1, size: 1000 });

  // Map: application_id -> user_id (owner)
  const applicationOwnerById = useMemo(() => {
    const map = new Map<string, string>();
    const apps = (allApplicationsData as any)?.items || [];
    for (const a of apps) {
      if (a?.id && a?.user_id) {
        map.set(a.id, a.user_id);
      }
    }
    return map;
  }, [allApplicationsData?.items]);

  // Map: user_id -> number of applications
  const applicationCountByUser = useMemo(() => {
    const map = new Map<string, number>();
    const apps = (allApplicationsData as any)?.items || [];
    for (const a of apps) {
      if (a?.user_id) {
        map.set(a.user_id, (map.get(a.user_id) || 0) + 1);
      }
    }
    return map;
  }, [allApplicationsData?.items]);

  // Map: application_id -> number of files
  const fileCountByApplication = useMemo(() => {
    const map = new Map<string, number>();
    const files = (allFilesData as any)?.items || [];
    for (const f of files) {
      if (f?.application_id) {
        map.set(f.application_id, (map.get(f.application_id) || 0) + 1);
      }
    }
    return map;
  }, [allFilesData?.items]);

  // Map: user_id -> total files across that user's applications
  const fileCountByUser = useMemo(() => {
    const map = new Map<string, number>();
    const files = (allFilesData as any)?.items || [];
    for (const f of files) {
      const ownerId = f?.application_id ? applicationOwnerById.get(f.application_id) : undefined;
      if (ownerId) {
        map.set(ownerId, (map.get(ownerId) || 0) + 1);
      }
    }
    return map;
  }, [allFilesData?.items, applicationOwnerById]);

  // Get current items based on path
  const currentItems = useMemo(() => {
    const items: ExplorerItem[] = [];
    // Helper: categorize files into common document groups
    const GROUP_DEFS: { key: string; name: string }[] = [
      { key: 'nid', name: 'NID' },
      { key: 'driver_license', name: 'Driver Licence' },
      { key: 'passport', name: 'Passport' },
      { key: 'borrower_photo', name: 'Borrower Photo' },
      { key: 'guarantor_photo', name: 'Guarantor Photo' },
      { key: 'other', name: 'Other Documents' },
    ];

    const getGroupKeyForFilename = (name: string): string => {
      const n = name.toLowerCase();
      if (/(\bnid\b|national\s*id|id\s*card|identity)/.test(n)) return 'nid';
      if (/(driver|driving|licen[cs]e)/.test(n)) return 'driver_license';
      if (/passport/.test(n)) return 'passport';
      if (/(borrower|selfie|profile|customer|applicant)/.test(n)) return 'borrower_photo';
      if (/(guarantor|surety)/.test(n)) return 'guarantor_photo';
      return 'other';
    };

    if (currentPath.length === 0) {
      // Root level - show customers
      const customers = customersData?.items || [];
      const mapped: CustomerFolder[] = customers.map((u: User) => ({
        id: u.id,
        name: `${u.first_name} ${u.last_name}`.trim(),
        type: 'customer',
        customer_id: u.id,
        application_count: applicationCountByUser.get(u.id) || 0,
        file_count: fileCountByUser.get(u.id) || 0,
        created_at: u.created_at,
      }));
      items.push(...mapped);
    } else if (currentPath.length === 1) {
      // Customer level - show applications
      const customerId = currentPath[0];
      const apps: ApplicationFolder[] = (applicationsList as CustomerApplication[]).map((a) => ({
        id: a.id,
        name: a.account_id ? `${a.account_id}` : `${a.product_type || 'Application'} (${a.id.slice(0, 8)})`,
        type: 'application',
        application_id: a.id,
        customer_id: customerId,
        file_count: fileCountByApplication.get(a.id) || 0,
        status: a.status,
        account_id: a.account_id,
        created_at: a.created_at,
      }));
      items.push(...apps);
    } else if (currentPath.length === 2) {
      // Application level
      // Prefer folders if they exist; otherwise, show files directly under the application
      const hasFolders = Array.isArray(foldersData) && foldersData.length > 0;
      if (hasFolders) {
        const appFolders: DocumentFolder[] = (foldersData || []).map((f) => ({
          id: f.id,
          name: f.name,
          type: 'folder' as const,
          application_id: f.application_id,
          parent_id: f.parent_id,
          file_count: f.file_count,
          created_at: f.created_at,
        }));
        items.push(...appFolders);
      } else if (filesData?.items) {
        // Build virtual group folders from files
        const counts: Record<string, { count: number; created_at: string }> = {};
        for (const f of filesData.items) {
          const key = getGroupKeyForFilename(f.original_filename);
          if (!counts[key]) counts[key] = { count: 0, created_at: f.created_at };
          counts[key].count += 1;
          // earliest created_at for display ordering
          if (new Date(f.created_at) < new Date(counts[key].created_at)) {
            counts[key].created_at = f.created_at;
          }
        }

        for (const def of GROUP_DEFS) {
          const info = counts[def.key];
          if (info && info.count > 0) {
            items.push({
              id: `group:${def.key}`,
              name: def.name,
              type: 'folder',
              application_id: currentApplicationId,
              parent_id: undefined,
              file_count: info.count,
              created_at: info.created_at,
            } as DocumentFolder);
          }
        }
      }
    } else if (currentPath.length === 3) {
      // Inside a folder or virtual group - show files
      if (filesData?.items) {
        const isVirtualGroup = currentFolderId?.startsWith('group:');
        const groupKey = isVirtualGroup ? currentFolderId?.slice('group:'.length) : '';

        const files: FileItem[] = filesData.items
          .filter(file => {
            if (!isVirtualGroup) return true; // real folders already filtered by API in useFiles
            const key = getGroupKeyForFilename(file.original_filename);
            return key === groupKey;
          })
          .map(file => ({ ...file, type: 'file' as const }));

        let filteredFiles = files;
        if (searchTerm) {
          filteredFiles = filteredFiles.filter(file =>
            file.original_filename.toLowerCase().includes(searchTerm.toLowerCase())
          );
        }

        items.push(...filteredFiles);
      }
    }

    return items;
  }, [currentPath, filesData?.items, searchTerm, customersData?.items, applicationsList, foldersData, applicationCountByUser, fileCountByUser, fileCountByApplication, currentFolderId, currentApplicationId]);

  const getStatusBadge = (status: string) => {
    const colors = {
      approved: 'bg-green-100 text-green-800',
      pending: 'bg-yellow-100 text-yellow-800', 
      submitted: 'bg-blue-100 text-blue-800',
      rejected: 'bg-red-100 text-red-800'
    };
    
    return (
      <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${colors[status as keyof typeof colors] || 'bg-gray-100 text-gray-800'}`}>
        {status}
      </span>
    );
  };

  const handleItemClick = (item: ExplorerItem) => {
    if (item.type === 'customer') {
      setCurrentPath([item.customer_id]);
      setSelectedItems(new Set());
    } else if (item.type === 'application') {
      setCurrentPath([item.customer_id, item.application_id]);
      setSelectedItems(new Set()); 
    } else if (item.type === 'folder') {
      if (currentCustomerId && currentApplicationId) {
        setCurrentPath([currentCustomerId, currentApplicationId, item.id]);
        setSelectedItems(new Set());
      }
    } else {
      // File item
      if (selectable) {
        setSelectedItems(new Set([item.id]));
        onFileSelect?.(item as FileItem);
      } else {
        const files = currentItems.filter(i => i.type === 'file') as FileItem[];
        const fileIndex = files.findIndex(f => f.id === item.id);
        setPreviewFiles(files);
        setCurrentPreviewIndex(fileIndex);
        setPreviewFile(item as FileItem);
      }
    }
  };

  const handleBreadcrumbClick = (index: number) => {
    setCurrentPath(currentPath.slice(0, index));
  };

  const handlePreviewNavigation = (direction: 'prev' | 'next') => {
    const newIndex = direction === 'prev' ? currentPreviewIndex - 1 : currentPreviewIndex + 1;
    if (newIndex >= 0 && newIndex < previewFiles.length) {
      setCurrentPreviewIndex(newIndex);
      setPreviewFile(previewFiles[newIndex]);
    }
  };

  const handleDelete = async () => {
    if (fileToDelete) {
      await deleteFileMutation.mutateAsync(fileToDelete.id);
      setFileToDelete(null);
      refetch();
    }
  };

  const getBreadcrumbPath = () => {
    const paths = [{ name: 'Customers', index: -1 }];
    
    if (currentPath.length > 0) {
      const customers = customersData?.items || [];
      const customer = (customers as User[]).find(c => c.id === currentPath[0]);
      if (customer) {
        const displayName = `${customer.first_name} ${customer.last_name}`.trim() || customer.username;
        paths.push({ name: displayName, index: 0 });
      }
      
      if (currentPath.length > 1) {
        const application = (applicationsList as CustomerApplication[]).find(a => a.id === currentPath[1]);
        if (application) {
          const name = application.account_id
            ? `${application.account_id}`
            : `${application.product_type || 'Application'} (${application.id.slice(0, 8)})`;
          paths.push({ name, index: 1 });
        }

        if (currentPath.length > 2) {
          const folder = (foldersData || []).find((f) => f.id === currentPath[2]);
          if (folder) {
            paths.push({ name: folder.name, index: 2 });
          }
        }
      }
    }
    
    return paths;
  };

  if (
    (currentPath.length === 0 && isLoadingCustomers) ||
    (currentPath.length === 1 && isLoadingApplications) ||
    (currentPath.length === 2 && (isLoadingFolders || isLoading)) ||
    (currentPath.length === 3 && isLoading)
  ) {
    return (
      <div className="flex items-center justify-center h-32">
        <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
      {/* Breadcrumb */}
      <div className="flex items-center px-4 py-2 bg-gray-50 border-b border-gray-200 text-sm">
        {getBreadcrumbPath().map((path, index) => (
          <div key={index} className="flex items-center">
            {index > 0 && <ChevronRightIcon className="h-4 w-4 mx-2 text-gray-400" />}
            <button
              onClick={() => handleBreadcrumbClick(path.index + 1)}
              className="flex items-center text-gray-600 hover:text-gray-900"
            >
              {index === 0 && <HomeIcon className="h-4 w-4 mr-2" />}
              {path.name}
            </button>
          </div>
        ))}
      </div>

      {/* Toolbar */}
      <div className="flex items-center justify-between px-4 py-3 bg-white border-b border-gray-200">
        <div className="flex items-center gap-4">
          <span className="text-sm text-gray-600">{currentItems.length} items</span>
          {selectedItems.size > 0 && (
            <span className="text-sm text-blue-600">({selectedItems.size} selected)</span>
          )}
        </div>

        <div className="flex items-center gap-4">
          {/* Search - only show when viewing files */}
          {currentPath.length === 3 && (
            <div className="relative">
              <MagnifyingGlassIcon className="h-4 w-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                placeholder="Search files..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 pr-4 py-1 text-sm border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent w-48"
              />
            </div>
          )}

          {/* View mode toggle - only show when viewing files */}
          {currentPath.length === 3 && (
            <div className="flex items-center gap-1">
              <button
                onClick={() => setViewMode('grid')}
                className={`p-2 rounded ${viewMode === 'grid' ? 'bg-blue-100 text-blue-600' : 'text-gray-500 hover:text-gray-700'}`}
                title="Grid view"
              >
                <Squares2X2Icon className="h-4 w-4" />
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={`p-2 rounded ${viewMode === 'list' ? 'bg-blue-100 text-blue-600' : 'text-gray-500 hover:text-gray-700'}`}
                title="List view"
              >
                <ListBulletIcon className="h-4 w-4" />
              </button>
            </div>
          )}

          <button
            onClick={() => refetch()}
            className="p-2 text-gray-500 hover:text-gray-700 rounded"
            title="Refresh"
          >
            <ArrowPathIcon className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="overflow-auto max-h-96">
        {currentItems.length === 0 ? (
          <div className="text-center py-12">
            <FolderIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500">
              {searchTerm ? 'No items match your search' : 'This folder is empty'}
            </p>
          </div>
        ) : currentPath.length <= 2 ? (
          /* Folder view for customers, applications, and folders */
          <div className="divide-y divide-gray-100">
            {currentItems.map((item) => (
              <div
                key={item.id}
                className="flex items-center px-4 py-3 hover:bg-blue-50 cursor-pointer"
                onClick={() => handleItemClick(item)}
              >
                <div className="flex items-center gap-3 flex-1 min-w-0">
                  {item.type === 'customer' ? (
                    <UserIcon className="h-8 w-8 text-blue-500" />
                  ) : item.type === 'application' ? (
                    <DocumentTextIcon className="h-8 w-8 text-green-500" />
                  ) : (
                    <FolderIcon className="h-8 w-8 text-yellow-500" />
                  )}
                  
                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {item.type === 'customer' || item.type === 'application' || item.type === 'folder'
                        ? (item as CustomerFolder | ApplicationFolder | DocumentFolder).name
                        : ''}
                    </p>
                    <div className="flex items-center gap-2 text-xs text-gray-500">
                      {item.type === 'customer' ? (
                        <>
                          <span>{(item as CustomerFolder).application_count} applications</span>
                          <span>•</span>
                          <span>{item.file_count} files</span>
                        </>
                      ) : item.type === 'application' ? (
                        <>
                          {(item as ApplicationFolder).account_id && (
                            <>
                              <span>Acct: {(item as ApplicationFolder).account_id}</span>
                              <span>•</span>
                            </>
                          )}
                          <span>{item.file_count} files</span>
                          <span>•</span>
                          {(item as ApplicationFolder).status && getStatusBadge((item as ApplicationFolder).status!)}
                        </>
                      ) : (
                        <>
                          <span>{(item as DocumentFolder).file_count} files</span>
                          <span>•</span>
                          <span>{formatDate(item.created_at)}</span>
                        </>
                      )}
                      {item.type !== 'folder' && (
                        <>
                          <span>•</span>
                          <span>{formatDate(item.created_at)}</span>
                        </>
                      )}
                    </div>
                  </div>
                </div>
                <ChevronRightIcon className="h-4 w-4 text-gray-400" />
              </div>
            ))}
          </div>
        ) : viewMode === 'grid' ? (
          /* Grid view for files */
          <div className="p-4">
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 xl:grid-cols-8 gap-4">
              {currentItems.map((item) => {
                const file = item as FileItem;
                return (
                  <div key={file.id} className="group">
                    <ImageThumbnail
                      file={file}
                      size="lg"
                      className="hover:shadow-md transition-shadow"
                      onClick={() => handleItemClick(file)}
                      showFileName={true}
                    />
                    
                    {showActions && (
                      <div className="flex justify-center gap-1 mt-2 opacity-0 group-hover:opacity-100 transition-opacity">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            downloadFile(file.id, file.original_filename);
                          }}
                          className="p-1 text-blue-600 hover:text-blue-800 text-xs"
                          title="Download"
                        >
                          <ArrowDownTrayIcon className="h-4 w-4" />
                        </button>
                        {(user?.role === 'admin' || file.uploaded_by === user?.id) && (
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              setFileToDelete(file);
                            }}
                            className="p-1 text-red-600 hover:text-red-800 text-xs"
                            title="Delete"
                          >
                            <TrashIcon className="h-4 w-4" />
                          </button>
                        )}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        ) : (
          /* List view for files */
          <div className="divide-y divide-gray-100">
            {currentItems.map((item) => {
              const file = item as FileItem;
              return (
                <div
                  key={file.id}
                  className="flex items-center px-4 py-3 hover:bg-blue-50 cursor-pointer"
                  onClick={() => handleItemClick(file)}
                >
                  <div className="flex items-center gap-3 flex-1 min-w-0">
                    <ImageThumbnail
                      file={file}
                      size="sm"
                    />
                    
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {file.original_filename}
                      </p>
                      <p className="text-xs text-gray-500">
                        {formatBytes(file.file_size)} • {formatDate(file.created_at)}
                      </p>
                    </div>
                  </div>

                  {showActions && (
                    <div className="flex items-center gap-2">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          downloadFile(file.id, file.original_filename);
                        }}
                        className="p-1 text-blue-600 hover:text-blue-800"
                        title="Download"
                      >
                        <ArrowDownTrayIcon className="h-4 w-4" />
                      </button>
                      {(user?.role === 'admin' || file.uploaded_by === user?.id) && (
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            setFileToDelete(file);
                          }}
                          className="p-1 text-red-600 hover:text-red-800"
                          title="Delete"
                        >
                          <TrashIcon className="h-4 w-4" />
                        </button>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* File Preview */}
      {previewFile && (
        <FilePreview
          file={previewFile}
          isOpen={!!previewFile}
          onClose={() => setPreviewFile(null)}
          files={previewFiles}
          currentIndex={currentPreviewIndex}
          onNavigate={handlePreviewNavigation}
        />
      )}

      {/* Delete Confirmation */}
      {fileToDelete && (
        <ConfirmDialog
          isOpen={!!fileToDelete}
          onClose={() => setFileToDelete(null)}
          onConfirm={handleDelete}
          title="Delete File"
          message={`Are you sure you want to delete "${fileToDelete.original_filename}"?`}
          confirmText="Delete"
          confirmButtonClass="bg-red-600 hover:bg-red-700"
        />
      )}
    </div>
  );
}

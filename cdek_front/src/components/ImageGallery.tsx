/* eslint-disable @next/next/no-img-element */
import React, { useState } from "react";
import { X, ZoomIn } from "lucide-react";
import { ImageResp } from "@/types/response";

interface ImageGalleryProps {
  images: ImageResp[];
}

export const ImageGallery: React.FC<ImageGalleryProps> = ({ images = [] }) => {
  const [selectedImage, setSelectedImage] = useState<ImageResp | null>(null);

  const openModal = (image: ImageResp) => {
    setSelectedImage(image);
  };

  const closeModal = () => {
    setSelectedImage(null);
  };

  const handleBackdropClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (e.target === e.currentTarget) {
      closeModal();
    }
  };

  if (!images || images.length === 0) {
    return (
      <div className="p-4 text-center text-gray-500">
        <p>Нет изображений для отображения</p>
      </div>
    );
  }

  return (
    <div>
      {/* Основная галерея */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
        {images.map((img, index) => (
          <div
            key={index}
            className="bg-gray-100 p-2 rounded hover:bg-gray-200 transition-colors"
          >
            <h4 className="text-sm font-medium text-gray-700 mb-2">
              {img.name}
            </h4>
            <div
              className="relative group cursor-pointer aspect-square"
              onClick={() => openModal(img)}
            >
              {/* Изменение: добавлен атрибут decoding="async" и объект-заполнитель */}
              <img
                src={`data:image/png;base64,${img.data}`}
                alt={img.name}
                className="w-full h-full object-contain rounded transition-transform group-hover:scale-105"
                decoding="async"
                onError={(e) => {
                  // Фоллбэк на прозрачный пиксель при ошибке загрузки
                  e.currentTarget.src = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=";
                }}
              />
              {/* Иконка увеличения при наведении */}
              <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-30 transition-all duration-200 rounded flex items-center justify-center">
                <ZoomIn
                  className="text-white opacity-0 group-hover:opacity-100 transition-opacity duration-200"
                  size={24}
                />
              </div>
            </div>
            <p className="text-xs text-gray-500 mt-1">
              Размер: {(img.size / 1024).toFixed(1)} KB
            </p>
          </div>
        ))}
      </div>

      {/* Модальное окно */}
      {selectedImage && (
        <div
          className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4"
          onClick={handleBackdropClick}
        >
          <div className="relative max-w-4xl max-h-full bg-white rounded-lg overflow-hidden">
            {/* Кнопка закрытия */}
            <button
              onClick={closeModal}
              className="absolute top-4 right-4 z-10 bg-white bg-opacity-80 hover:bg-opacity-100 rounded-full p-2 transition-all"
            >
              <X size={20} className="text-gray-700" />
            </button>

            {/* Заголовок */}
            <div className="bg-gray-50 px-6 py-4 border-b">
              <h3 className="text-lg font-semibold text-gray-800">
                {selectedImage.name}
              </h3>
              <p className="text-sm text-gray-500">
                Размер: {(selectedImage.size / 1024).toFixed(1)} KB
              </p>
            </div>

            {/* Изображение */}
            <div className="p-4">
              <img
                src={`data:image/png;base64,${selectedImage.data}`}
                alt={selectedImage.name}
                className="max-w-full max-h-[70vh] object-contain mx-auto"
                // Добавлено для предотвращения проблем с отображением
                decoding="async"
                onError={(e) => {
                  // Фоллбэк на прозрачный пиксель при ошибке загрузки
                  e.currentTarget.src = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=";
                }}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
